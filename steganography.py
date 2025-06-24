from PIL import Image
import numpy as np

# Utility: Convert text to binary
def text_to_binary(text):
    return ''.join([format(ord(char), '08b') for char in text])

# Utility: Convert binary to text
def binary_to_text(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join([chr(int(char, 2)) for char in chars])

# Encode message in image
def encode_image(input_image_path, output_image_path, secret_message):
    # Add delimiter to message
    secret_message += '####'  # unique end-of-message delimiter
    binary_msg = text_to_binary(secret_message)

    img = Image.open(input_image_path)
    img = img.convert('RGB')
    np_img = np.array(img)

    flat_pixels = np_img.flatten()
    if len(binary_msg) > len(flat_pixels):
        raise ValueError("Message too long for this image.")

    for i in range(len(binary_msg)):
        flat_pixels[i] = (flat_pixels[i] & ~1) | int(binary_msg[i])

    new_pixels = flat_pixels.reshape(np_img.shape)
    new_img = Image.fromarray(new_pixels.astype('uint8'), 'RGB')
    new_img.save(output_image_path)
    print(f"[+] Message encoded and saved as {output_image_path}")

# Decode message from image
def decode_image(stego_image_path):
    img = Image.open(stego_image_path)
    img = img.convert('RGB')
    np_img = np.array(img)

    flat_pixels = np_img.flatten()
    binary_data = ''.join([str(pixel & 1) for pixel in flat_pixels])

    # Split into 8-bit chunks
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ''
    for char in chars:
        message += chr(int(char, 2))
        if message.endswith('####'):
            break
    return message.replace('####', '')

# Command-line interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="LSB Image Steganography Tool")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Encode
    encode_parser = subparsers.add_parser('encode', help='Hide a message in an image')
    encode_parser.add_argument('-i', '--input', required=True, help='Input image path')
    encode_parser.add_argument('-o', '--output', required=True, help='Output stego-image path')
    encode_parser.add_argument('-m', '--message', required=True, help='Secret message to hide')

    # Decode
    decode_parser = subparsers.add_parser('decode', help='Extract a hidden message from an image')
    decode_parser.add_argument('-i', '--input', required=True, help='Input stego-image path')

    args = parser.parse_args()

    if args.command == 'encode':
        encode_image(args.input, args.output, args.message)
    elif args.command == 'decode':
        message = decode_image(args.input)
        print("[+] Hidden Message:")
        print(message)
    else:
        parser.print_help()
