import re
from typing import Optional

from .constants import exclude_phone_number_list


def clean_phone(
    phone: str, exclude_numbers: Optional[list] = None, delimiter: str = "|"
) -> Optional[str]:
    """Cleans phone numbers and outputs a list of valid phone numbers.

    Parameters
    ----------
    phone: str
        A string representation of phone number(s).
        The phone numbers can be concatenated together with the `|` character.
        The range of numbers (with the dash, -) can also be used.
        For example,
            phone = '090-123-4567|0912345678'
            phone = '0901234567-9'

        It also removes any numbers that start with '000' or presented in `exclude_phone_number_list`.

    exclude_numbers: Optional[list], default=None
        List of numbers to exclude.
        If not specified (None), it uses the default values in `exclude_phone_number_list`.
        If you do not want to exclude any numbers, put in an empty list.

    delimiter: str, default="|"
        A delimiter character to separate phone numbers.

    Returns
    -------
    str | None
        Valid phone number(s), concatnated with `|` character.
    """

    if exclude_numbers is not None and not isinstance(exclude_numbers, list):
        raise ValueError("`exclude_numbers` must be a list or None")

    exclude_numbers = (
        exclude_phone_number_list if exclude_numbers is None else exclude_numbers
    )

    if not phone:
        return None

    phone = re.sub(r"\s|\(|\)|\+", "", phone)  # Remove '(', ')', spaces, and '+' sign
    # Split the text by the comma, in case there are multiple numbers
    phone_arr = phone.split(delimiter)

    phone_pat = r"^[-\d]+"  # Search and keep for numbers, possibly with dashes

    ret_arr = []
    for ele in phone_arr:
        match = re.search(
            pattern=phone_pat, string=ele
        )  # Search and keep for numbers, possibly with dashes
        if match:
            phone_num = match.group()  # Get the matched phone number
            phone_num = re.sub(
                r"-(?=\d{3,})", "", phone_num
            )  # Replace the dash ('-') in the phone number, only if it's followed by 3 digits or more

            # Take care the case where the number has dash ('-') at the end, e.g., 0881112222-25
            # Please note that at this point, there may still be dashes left in the string, e.g., 081-23-45678 (if the dash is followed by fewer than 3 digits)
            if phone_num[-3:][0] == "-":
                number_before_last_two_digits = phone_num[:-5]
                last_two_digits = phone_num[-5:-3]
                until_two_digits = phone_num[-2:]
                try:  # Try converting and concatenating the numbers
                    num_arr = [
                        re.sub(r"-", "", number_before_last_two_digits + str(ii))
                        for ii in range(int(last_two_digits), int(until_two_digits) + 1)
                    ]  # Also, finally, replace all the dashes left in the string
                    ret_arr.extend(num_arr)
                except Exception as e:  # If fails, just cut out the last part
                    print(f"Failed to convert last digits to int: {e}")
                    ret_arr.append(re.sub(r"-", "", phone_num[:-3]))

            elif phone_num[-2:][0] == "-":
                number_before_last_digit = phone_num[:-3]
                last_digit = phone_num[-3:-2]
                until_digit = phone_num[-1:]
                try:  # Try converting and concatenating the numbers
                    num_arr = [
                        re.sub(r"-", "", number_before_last_digit + str(ii))
                        for ii in range(int(last_digit), int(until_digit) + 1)
                    ]  # Also, finally, replace all the dashes left in the string
                    ret_arr.extend(num_arr)
                except Exception as e:  # If fails, just cut out the last part
                    print(f"Failed to convert last digits to int: {e}")
                    ret_arr.append(re.sub(r"-", "", phone_num[:-2]))

            else:
                ret_arr.append(phone_num)

    if not ret_arr:  # Check if there are any elements in the ret_arr
        return None

    # Final pattern match for phone numbers
    final_ret_arr = []
    prefix_pat = r"^\+?66"
    final_phone_pat = r"\d{9,10}"

    for ele in ret_arr:
        ele_cleaned = re.sub(prefix_pat, "0", ele)
        match = re.search(pattern=final_phone_pat, string=ele_cleaned)

        if match:
            phone_num = match.group()

            if phone_num not in exclude_numbers and not phone_num.startswith("000"):
                final_ret_arr.append(phone_num)

    final_phone = delimiter.join(final_ret_arr)

    return final_phone if final_phone else None
