from feedgen.feed import FeedGenerator
import datetime

def postfeed(fromlib):

    f = FeedGenerator()

    f.title('FPH deleted posts')
    f.link( href='https://voat.co/v/fatpeoplehate/modlog/deleted', rel='alternate' )
    f.subtitle('Posts deleted by FPH mods')
    f.language('en')

    for i in fromlib.split('Removed by'):
        list = i.split('\n')
        rline = list[0].split()

        if len(rline) < 1:
            continue

        user = rline[0]
        print rline
        date_str = rline[2] + ' ' + rline[3] + ' ' + rline[4].strip('.') + ' UTC'

        reason = 'Feature not impmenented'

        for line in list:
            if '<a class="title may-blank "' in line:
                iline = line.split()
                url = iline[4].split('=', 1)[1].strip('"')

                if url.startswith('/v/'):
                    url = 'https://voat.co' + url

                title = ''

                for word in iline[6:int(((len(iline) - 6) / 2) + 7)]:
                    title += word + ' '

                title = title.split('"')[1]
                break

        entry = f.add_entry()
        entry.link({'href': url})
        entry.title(title)
        entry.author({'name':'https://voat.co/user/' + user, 'email': user})
        print date_str
        entry.published(date_str)
        entry.summary('Banned by %s, Reason: %s' % (user, reason))

    return f.rss_str(pretty=True)

def commentfeed(fromlib):

    f = FeedGenerator()

    f.title('FPH deleted comments')
    f.link( href='https://voat.co/v/fatpeoplehate/modlog/deletedcomments', rel='alternate' )
    f.subtitle('Comments deleted by FPH mods')
    f.language('en')

    for i in fromlib.split('Removed by'):
        list = i.split('\n')
        rline = list[0].split()

        if len(rline) < 1:
            continue

        user = rline[0]
        date_str = rline[2] + ' ' + rline[3] + ' ' + rline[4].strip('.') + ' UTC'

        reason = 'Feature not impmenented'

        for line in list:
            if 'permalink' in line:
                iline = line.split()
                url = iline[1].split('=', 1)[1].strip('"')

                if url.startswith('/v/'):
                    url = 'https://voat.co' + url

                title = ''

                #for word in iline[6:int(((len(iline) - 6) / 2) + 7)]:
                #    title += word + ' '
                #
                #title = title.split('"')[1]
                break

        entry = f.add_entry()
        entry.link({'href': url})
        entry.title(title)
        entry.author({'name':'https://voat.co/user/' + user, 'email': user})
        entry.published(date_str)
        entry.summary('Banned by %s, Reason: %s' % (user, reason))

    return f.rss_str(pretty=True)
