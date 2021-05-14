${confog_path} = "./cfg/yolov2-tiny-voc-lab9.cfg"



python flow `
    --model "${confog_path}" `
    --load -1 `
    --savepb
