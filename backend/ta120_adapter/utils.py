import json


def dump_laeq1s_registers(value: str) -> str:
    """
    Dump the LAeq1s registers value as a JSON list.

    The input value is expected to be a LAeq1s registers value of Cesva
    TA120 sensor, which is in the following format:

        046.6,0,0;048.4,0,0;047.4,0,0;043.3,0,0;039.9,0,0;039.8,0,0

    So there are triplets of a float and two ints separated by
    semicolons (;) and the values inside the triplets are separated by
    commas (,).

    This function will reformat that value as a list of lists in JSON,
    i.e. the above example will be converted to:

        [[46.6,0,0],[48.4,0,0],[47.4,0,0],[43.3,0,0],[39.9,0,0],[39.8,0,0]]

    Another example (in a doctest format):

        >>> dump_laeq1s_registers('046.6,0,0;248.0,1,0;007.1,0,1')
        '[[46.6,0,0],[248.0,1,0],[7.1,0,1]]'
    """
    registers = [
        [float(num) if '.' in num else int(num)
         for num in item.strip().split(',')]
        for item in value.strip().split(';')]
    return json.dumps(registers, separators=(',', ':'))
