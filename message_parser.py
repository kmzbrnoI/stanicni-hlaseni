def parse(data, separators):
    output = []
    item = ''
    escaped_level = 0

    separators = [';', '[', ']']

    for i in range(len(data)):
        active = data[i]

        if active == '{':

            if escaped_level > 0:
                item += active
            escaped_level += 1

        elif (active == '}') and (escaped_level > 0):
            escaped_level -= 1
            if (escaped_level > 0):
                item += active
        else:

            if (active in separators) and (escaped_level == 0):

                output.append(item)
                item = ''

            else:

                if (active not in separators) or (escaped_level > 0):
                    item += active

    if (item != ""):
        output.append(item)

    return output
