def reform_crochet_pattern(pattern):
    """
    Reformats the crochet pattern by compressing consecutive identical stitches into a single entry with a count.

    Parameters:
    pattern (str): The crochet pattern string consisting of stitch types separated by commas.
    
    Returns:
    str: The reformatted crochet pattern with stitch counts.
    """
    # Split the input pattern by commas and trim any extra spaces
    stitches = [s.strip() for s in pattern.split(',') if s.strip()]

    # Initialize variables
    current_stitch = stitches[0] if stitches else ''
    count = 1
    result = []

    # Iterate over the stitches array
    for i in range(1, len(stitches)):
        if stitches[i] == current_stitch:
            # Increment count if the current stitch is the same as the previous
            count += 1
        else:
            # Append the current stitch and its count to the result
            if count > 1:
                result.append(f'{current_stitch} x{count}')
            else:
                result.append(current_stitch)
            # Update current stitch and reset count
            current_stitch = stitches[i]
            count = 1

    # Add the last stitch and its count
    if count > 1:
        result.append(f'{current_stitch} x{count}')
    else:
        result.append(current_stitch)

    # Join the result list into a single string with ', ' as separator
    return ', '.join(result)