from blinker import Namespace

ns = Namespace()

file_uploaded = ns.signal('file-uploaded')

file_deleted = ns.signal('file-deleted')

before_display = ns.signal('before-display')
