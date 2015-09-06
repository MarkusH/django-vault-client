from gnupg import GPG as GnuPG


class GPG(GnuPG):

    def __init__(self, *args, **kwargs):
        super(GPG, self).__init__(*args, **kwargs)
