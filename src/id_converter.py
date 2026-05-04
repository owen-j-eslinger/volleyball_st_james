
import base64

def url_id_to_numeric(encoded_id):
    """
    Converts a URL ID (PTAw...) to a numeric backend ID (41287).
    Includes error handling for malformed or corrupted strings.
    """
    try:
        # 1. Replace the custom padding '90' back to '='
        padding_fixed = str(encoded_id).replace('90', '=')

        # 2. Base64 decode the string
        decoded_bytes = base64.b64decode(padding_fixed)
        decoded_str = decoded_bytes.decode('utf-8')

        # 3. Strip leading '=' and convert to integer
        clean_numeric_str = decoded_str.lstrip('=')
        return int(clean_numeric_str)
    
    except Exception as e:
        # Provide a descriptive error for easier debugging in logs
        raise ValueError(f"Decoding failed for ID '{encoded_id}': {e}")

def numeric_to_url_id(numeric_id):
    """
    Converts a numeric ID (41287) to a URL ID (PTAw...).
    """
    try:
        # 1. Prepends '=' and pads the number to 10 digits as per system requirements
        raw_str = f"={str(numeric_id).zfill(10)}"

        # 2. Base64 encode the string
        encoded_bytes = base64.b64encode(raw_str.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')

        # 3. Replace the standard '=' padding with '90'
        return encoded_str.replace('=', '90')
    
    except Exception as e:
        raise ValueError(f"Encoding failed for numeric value '{numeric_id}': {e}")

# This block allows you to run tests directly from this file
if __name__ == "__main__":
    print("--- Running ID Converter Unit Tests ---")
    test_url_id = "PTAwMDAwNDEyODc90"
    test_numeric_id = 41287
    
    try:
        num_id = url_id_to_numeric(test_url_id)
        print(f"Successfully Converted to Numeric ID: {num_id}")
        print(f"Original                  Numeric ID: {test_numeric_id}")
        # Verify it goes back the other way
        print(f"\nVerifying reverse conversion for {test_numeric_id}...")
        back_to_url = numeric_to_url_id(test_numeric_id)
        print(f"Back to  URL ID: {back_to_url}")
        print(f"Original URL ID: {test_url_id}")
        
    except Exception as error:
        print(f"Test Failed: {error}")
