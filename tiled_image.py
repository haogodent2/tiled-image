import os
from time import sleep
from PIL import Image, ImageStat
from scipy import spatial

cwd = os.path.abspath(os.path.dirname(__file__))
#cwd = "/Users/haochen/Documents/tiled-image"

cell_size = (40, 40)
resize_tag = "resized_"

def main():
 	# assume jpgs for now
	
	res_imgs_dir_path = os.path.abspath(os.path.join(cwd, "res_images"))
	target_img_dir_path = os.path.abspath(os.path.join(cwd, "target"))

	res_imgs_list = os.listdir(res_imgs_dir_path)
	res_imgs_list = [item for item in res_imgs_list if not item.startswith('.')]

	# initialize img/median color dict
	#res_imgs_color_dict = dict(zip(res_imgs_list, [[0, 0, 0]]*len(res_imgs_list)))
	res_imgs_color_list = [[0, 0, 0]]*len(res_imgs_list)

	print("creating tiles and profiling their color...")
	# extract median color of each image and reize each according to cell size
	for img_name in res_imgs_list:
		img_path = os.path.join(res_imgs_dir_path, img_name)
		img = Image.open(img_path)

		img_median_color = ImageStat.Stat(img).median 
		
		#res_imgs_color_dict[img_name] = img_median_color
		res_imgs_color_list[res_imgs_list.index(img_name)] = img_median_color

		img_resized = img.resize(cell_size)
		img_resized_file = os.path.join(res_imgs_dir_path, resize_tag+img_name)
		#print("saving " + resize_tag+img_name)
		img_resized.save(img_resized_file, "JPEG" )

	# build spatial KDTree for nearest color neighbor lookup later
	#median_color_list = list(res_imgs_color_dict.values())
	median_color_tree = spatial.KDTree(res_imgs_color_list)

	# import target image
	target_img_name = os.listdir(target_img_dir_path)
	target_img_name= [item for item in target_img_name if not item.startswith('.')]
	target_img_path = os.path.join(target_img_dir_path, target_img_name[0])

	target_img = Image.open(target_img_path)
	#target_img = target_img.resize((2000, 2000))
	#create canvas for composite image
	composite_img = Image.new('RGB', ((target_img.width//cell_size[0])*cell_size[0], (target_img.height//cell_size[1])*cell_size[1]))
	print("scanning target image and creating the composite image...")
	for x in range(0, target_img.size[0], cell_size[0]):
		for y in range(0, target_img.size[1], cell_size[1]):
			#(col, row, col, row), (left, upper, right, lower) defines the window
			cropped_img = target_img.crop((x, y, x + cell_size[0], y + cell_size[1]))
			cropped_median = ImageStat.Stat(cropped_img).median
			results = median_color_tree.query(cropped_median)
			#open selected image, results~(error, index)
			temp_img = Image.open(os.path.join(res_imgs_dir_path, resize_tag+res_imgs_list[results[1]]))
			#paste into composite_image
			composite_img.paste(temp_img,(x, y))

	img_resized_file = os.path.join(cwd, "composite_image.jpg")
	composite_img.save(img_resized_file, "JPEG" )

	print("removing old files...")
	res_imgs_list = os.listdir(res_imgs_dir_path)
	res_imgs_list_to_delete = [item for item in res_imgs_list if item.startswith(resize_tag)]
	for item in res_imgs_list_to_delete:
		os.remove(os.path.join(res_imgs_dir_path, item))
	print("all done!")

if __name__ == "__main__": 
	main()
