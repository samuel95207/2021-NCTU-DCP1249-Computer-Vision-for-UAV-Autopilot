cd darkflow-master
python flow `
    --model cfg/yolo.cfg `
    --load bin/yolov2.weights `
    --imgdir sample_img/ `
    --gpu 1.0