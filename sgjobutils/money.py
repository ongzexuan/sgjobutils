
def filter_money(amount):
    if amount < 100:
        return -1
    return amount


def get_money(token):

    tokens = token.split("-")
    final_amt = -1
    if len(tokens) == 2:
        first = get_money_from_single_word(tokens[0])
        second = get_money_from_single_word(tokens[1])

        if first > 0 and second > 0:
            final_amt = int((first + second) / 2.0)
        elif first > 0:
            num = get_numeric(tokens[1])
            if num > 0:
                final_amt = int((first + num) / 2.0)
        elif second > 0:
            num = get_numeric(tokens[0])
            if num > 0:
                final_amt = int((num + second) / 2.0)
    else:
        final_amt = get_money_from_single_word(token)

    return filter_money(final_amt)


def get_money_from_single_word(word):
    """
    Obtain the numeric value of a money string if it is a money string

    :param word: string potentially containing monetary amount
    :return: integer indicating the monetary value of the string, else -1
    """

    word = word.lower().strip()
    pos = word.rfind("$")

    # Defensive programming
    if pos == len(word) - 1:
        return False

    # Word does not contain dollar sign
    money_string = ""
    kmultiply = False
    if pos < 0:
        # Is not money string
        if not word.endswith("k"):
            return -1

        start_pos = len(word) - 2
        while start_pos >= 0 and (word[start_pos].isdigit() or word[start_pos] == "," or word[start_pos] == "."):
            start_pos -= 1
        start_pos += 1

        money_string = word[start_pos: len(word) - 1]
        kmultiply = True
    else:
        end_pos = pos + 1
        while end_pos < len(word) and (word[end_pos].isdigit() or word[end_pos] == "," or word[end_pos] == "."):
            end_pos += 1

        if end_pos < len(word) and word[end_pos] == "k":
            kmultiply = True

        money_string = word[pos + 1: end_pos]

    stripped = comma_removal(money_string)

    # Somehow failed to get numeric value
    if not stripped.replace(".", "").isdigit():
        return -1

    amount = float(stripped)
    if kmultiply:
        amount *= 1000

    return int(amount)


def comma_removal(token):
    return token.replace(",", "")


def get_numeric(token):

    token = token.lower()
    if token.endswith("k"):
        if token[:-1].isdigit():
            return int(token[:-1]) * 1000
    else:
        if token.isdigit():
            return int(token)
    return -1
