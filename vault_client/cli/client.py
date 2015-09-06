#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import join

import click

from .utils import pretty_print_item, pretty_print_key
from ..lib.api import API
from ..lib.config import Config
from ..lib.gpg import GPG
from ..lib.vault import Item, Key


class Context(object):

    def __init__(self):
        self.gpg = None
        self.configdir = click.get_app_dir('django-vault')
        self.config = Config.load(join(self.configdir, 'clientrc'))


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@pass_context
def cli(ctx):
    ctx.gpg = GPG(homedir=ctx.config.homedir, use_agent=True)
    if click.get_current_context().invoked_subcommand != 'configure':
        ctx.api = API(host=ctx.config.hostname)
        ctx.api.login(username=ctx.config.username, password=ctx.config.password)


@cli.command()
@click.option('--hostname', prompt='Hostname')
@click.option('--username', prompt='Username')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True)
@click.option('--homedir', prompt='GnuPG Home')
@pass_context
def configure(ctx, hostname, username, password, homedir):
    ctx.config.hostname = hostname
    ctx.config.username = username
    ctx.config.password = password
    ctx.config.homedir = homedir
    ctx.config.save()


@cli.group()
@pass_context
def items(ctx):
    pass


@items.command(name='list')
@pass_context
def items_list(ctx):
    items = ctx.api.get_items()

    if items:
        click.secho("%36s  %21s  %-21s" % ("UUID", "Name", "Added / Last Modified"))
        for item in items:
            click.secho("%36s  %21s  %21s" % (item.uuid, item.name, item.date_updated.isoformat(' ')))
    else:
        click.secho('No items', fg='red')


@items.command(name='show')
@click.argument('uuid')
@pass_context
def items_show(ctx, uuid):
    item = ctx.api.get_item(uuid)
    pretty_print_item(item)

    try:
        import pyperclip
    except Exception:
        pass
    else:
        value = ctx.gpg.decrypt(item.value)
        if value.ok:
            value = value.data.decode('utf-8')
            pyperclip.copy(value)
            click.secho('The content has been copied to your clipboard', fg='green')
        else:
            click.secho(value.status, fg='red')
            click.secho(value.stderr)


@items.command(name='add')
@click.option('--name', prompt='Name')
@click.option('--value', prompt='Value', hide_input=True)
@pass_context
def items_add(ctx, name, value):
    item = Item(name=name, value=value)
    item._encrypted = False
    ctx.api.save_item(item)
    pretty_print_item(item)


@items.command(name='delete')
@click.argument('uuid')
@click.confirmation_option(prompt='Are you sure you want to delete this item?')
@pass_context
def items_delete(ctx, uuid):
    ctx.api.delete_item(uuid)


def default_item_name():
    current = click.get_current_context()
    ctx = current.obj
    ctx.item = ctx.api.get_item(current.params['uuid'])
    return ctx.item.name


@items.command(name='edit')
@click.argument('uuid')
@click.option('--name', prompt='Name', default=default_item_name)
@click.option('--value', prompt='Value', hide_input=True)
@pass_context
def items_edit(ctx, uuid, name, value):
    ctx.item.name = name
    ctx.item.value = value
    ctx.item._encrypted = False
    ctx.api.save_item(ctx.item)
    pretty_print_item(ctx.item)


@cli.group()
@pass_context
def keys(ctx):
    pass


@keys.command(name='list')
@pass_context
def keys_list(ctx):
    keys = ctx.api.get_keys()
    if keys:
        click.secho("%36s  %50s  %-21s" % ("UUID", "Fingerprint", "Added / Last Modified"))
        for key in keys:
            click.secho("%36s  %50s  %21s" % (key.uuid, key.fingerprint, key.date_updated.isoformat(' ')))
    else:
        click.secho('No keys', fg='red')


@keys.command(name='show')
@click.argument('uuid')
@pass_context
def keys_show(ctx, uuid):
    key = ctx.api.get_key(uuid)
    pretty_print_key(key)


@keys.command(name='add')
@click.option('--key', prompt='Key')
@pass_context
def keys_add(ctx, key):
    key = Key(key=key)
    ctx.api.save_key(key)
    pretty_print_key(key)


@keys.command(name='delete')
@click.argument('uuid')
@click.confirmation_option(prompt='Are you sure you want to delete this key?')
@pass_context
def keys_delete(ctx, uuid):
    ctx.api.delete_key(uuid)


def default_key_key():
    current = click.get_current_context()
    ctx = current.obj
    ctx.key = ctx.api.get_key(current.params['uuid'])
    return ctx.key.key


@keys.command(name='edit')
@click.argument('uuid')
@click.option('--key', prompt='Name', default=default_key_key)
@pass_context
def keys_edit(ctx, uuid, key):
    ctx.key.key = key
    ctx.key._encrypted = False
    ctx.api.save_key(ctx.key)
    pretty_print_key(ctx.key)


if __name__ == '__main__':
    cli()
