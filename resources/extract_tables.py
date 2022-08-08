import os
import cv2

def find_tables(image):
    '''
    blurs the image to reduce noise
    blur size & deviations are defined
    '''
    BLUR_KERNEL_SIZE = (17, 17)
    STD_DEV_X_DIRECTION = 0
    STD_DEV_Y_DIRECTION = 0
    blurred = cv2.GaussianBlur(image, BLUR_KERNEL_SIZE, STD_DEV_X_DIRECTION, STD_DEV_Y_DIRECTION)
    '''
    creates an image bin containing:

    ~blurred, #the blurred image
        MAX_COLOR_VAL, #number to set if threshold is exceeded
        cv2.ADAPTIVE_THRESH_MEAN_C, # threshold is set by average of local area
        cv2.THRESH_BINARY, #converts to binary black/white
        BLOCK_SIZE, # pixel neighbourhood to calc threshold
        SUBTRACT_FROM_MEAN,
    '''
    MAX_COLOR_VAL = 255
    BLOCK_SIZE = 15
    SUBTRACT_FROM_MEAN = -2
    
    img_bin = cv2.adaptiveThreshold(
        ~blurred,
        MAX_COLOR_VAL,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        BLOCK_SIZE,
        SUBTRACT_FROM_MEAN,
    )
    '''
    create horizontal and vertical versions of the image bin

    kernel = structure of the image

    opened =  processed to remove noise

    dilated = increases the white region around parts of the image, rejoins broken text
    '''
    vertical = horizontal = img_bin.copy()
    SCALE = 5
    
    image_width, image_height = horizontal.shape
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(image_width / SCALE), 1))
    horizontally_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, horizontal_kernel)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(image_height / SCALE)))
    vertically_opened = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, vertical_kernel)
    
    horizontally_dilated = cv2.dilate(horizontally_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1)))
    vertically_dilated = cv2.dilate(vertically_opened, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))
    '''
    detects change of image colour  and stores these areas
    '''
    mask = horizontally_dilated + vertically_dilated
    contours, heirarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )
    '''
    contours = filter contours down to ones with a big enough area for a table
    perimeter_lengths = perimeters of the remaining contours
    epsilons = approximate accuracy
    approx_polys = approximate polygons of the exisiting contours (w/ less vertices)
    bounding_rects = best fitting rectangle of the polygon area
    '''
    MIN_TABLE_AREA = 1e5
    for c in contours:
        print(cv2.contourArea(c))
    contours = [c for c in contours if cv2.contourArea(c) > MIN_TABLE_AREA]
    perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
    epsilons = [0.1 * p for p in perimeter_lengths]
    approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]
    bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

    # The link where a lot of this code was borrowed from recommends an
    # additional step to check the number of "joints" inside this bounding rectangle.
    # A table should have a lot of intersections. We might have a rectangular image
    # here though which would only have 4 intersections, 1 at each corner.
    # Leaving that step as a future TODO if it is ever necessary.
    '''
    adds each best fitting rectangle as an image to a list of images
    '''
    images = [image[y:y+h, x:x+w] for x, y, w, h in bounding_rects]
    return images

def main(files):
    results = []
    '''
    For each file in directory:
        converts to grayscale image
        extracts tables from image using above function
        stores all tables as pngs
    '''
    for f in files:
        directory, filename = os.path.split(f)
        print(f)
        image = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        tables = find_tables(image)
        files = []
        filename_sans_extension = os.path.splitext(filename)[0]
        if tables:
            os.makedirs(os.path.join(directory, filename_sans_extension), exist_ok=True)
        for i, table in enumerate(tables):
            table_filename = "table-{:03d}.png".format(i)
            table_filepath = os.path.join(
                directory, filename_sans_extension, table_filename
            )
            files.append(table_filepath)
            cv2.imwrite(table_filepath, table)
        if tables:
            results.append((f, files))
        else:
            print('No Tables Found')
    # Results is [[<input image>, [<images of detected tables>]]]
    return results

#main([r'C:\Users\jacks\Documents\GitHub\OCR-PDF-Mining\output\bin\Filtered PDF Images\04320853-1.png'])