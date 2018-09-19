from django.contrib.humanize.templatetags.humanize import ordinal


def possessive_state(state_label):
    if state_label[-1] == "s":
        return "{}’".format(state_label)
    return "{}’s".format(state_label)


def format_office_label(office, division_label):
    """
    Format the label for office into something we like for twitter.
    """
    if office.body:
        if office.body.slug == "senate":
            return "the Senate in {}".format(division_label)
        else:
            if office.division.code == "00":
                return "the House seat in {} at-large district".format(
                    possessive_state(division_label)
                )
            else:
                return "the House seat in {} {} District".format(
                    possessive_state(division_label),
                    ordinal(office.division.code),
                )
    else:
        # TODO: President
        return "governor in {}".format(division_label)
    return office.label
