import argparse
import os
from PIL import Image, ImageDraw
from psd_tools import PSDImage
from psd_tools.api.effects import ColorOverlay
import randomcolor

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", metavar='INPUT_PATH', type=str, required=True, help="The path of PSD file.")
parser.add_argument("-o", "--output", metavar="OUTPUT_PATH", type=str, help="Output path.")
parser.add_argument("-m", "--method", type=str, choices=["instance", "class"], required=True, help="Label by class or instance.")

IMG_SIZE = (5472, 3648)

def label_by_class(psd):
    seg = Image.new('RGBA', IMG_SIZE)
    rand_color = randomcolor.RandomColor()
    for layer in psd.descendants():
        if not layer.is_group():
            continue
        c_str = rand_color.generate(format_='rgb')[0]

        for sub_layer in layer.descendants():
            bbox = sub_layer.bbox
            layer_img = sub_layer.topil()
            if(layer_img.mode != "RGBA"):
                continue
            channels = layer_img.split()
            current_seg = Image.new('RGB', sub_layer.size, c_str)
            seg.paste(current_seg, bbox, channels[3])
    return seg

def label_by_instance(psd):
    seg = Image.new('RGBA', IMG_SIZE)
    rand_color = randomcolor.RandomColor()
    for layer in psd.descendants():
        if layer.is_group():
            continue
        c_str = rand_color.generate(format_='rgb')[0]
        
        bbox = layer.bbox
        layer_img = layer.topil()
        if(layer_img.mode != "RGBA"):
            continue
        channels = layer_img.split()
        current_seg = Image.new('RGB', layer.size, c_str)
        seg.paste(current_seg, bbox, channels[3])
    return seg

def main():
    # Testing basic functionality of the psd_utils
    args = parser.parse_args()
    psd_files = []
    if os.path.isfile(args.input):
        psd_files.append(args.input)
    else:
        psd_file_list = os.listdir(args.input).sort()
        psd_files = [f for f in psd_file_list if f.endswith(".psd") ]
    
    for psd_file in psd_files:
        psd = PSDImage.open(psd_file)
        if args.method == "instance":
            seg = label_by_instance(psd)
        elif args.method == "class":
            seg = label_by_class(psd)
        else:
            seg = None
            print("Not implemented.")

        if seg is not None:
            if os.path.isfile(args.output):
                seg.save(args.output)
            else:
                os.makedirs(args.output, exist_ok=True)
                head, tail = os.path.split(psd_file)
                filename = tail.replace(".psd", ".png")
                outpath = os.path.join(args.output, filename)
                seg.save(outpath)

def test_instance():
    psd = PSDImage.open("/Users/yujiew/Downloads/DSC05291.psd")
    instance_seg = label_by_instance(psd)

def test_class():
    psd = PSDImage.open("/Users/yujiew/Downloads/DSC05291.psd") 
    class_seg = label_by_class(psd)

if __name__ == "__main__":
    main()