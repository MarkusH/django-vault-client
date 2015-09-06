import click


def pretty_print_item(item):
    FORMAT = "%-12s: %s"
    for attr in ('uuid', 'name', 'date_added', 'date_updated'):
        click.secho(FORMAT % (attr.replace('_', ' ').title(), getattr(item, attr)))
    click.secho(FORMAT % ('Value', '\n'))
    click.secho(item.value.decode('utf-8'))


def pretty_print_key(key):
    FORMAT = "%-12s: %s"
    for attr in ('uuid', 'key', 'fingerprint', 'date_added', 'date_updated'):
        click.secho(FORMAT % (attr.replace('_', ' ').title(), getattr(key, attr)))
