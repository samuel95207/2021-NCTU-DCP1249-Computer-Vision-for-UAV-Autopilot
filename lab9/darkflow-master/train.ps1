${annotation_path} = "../dataset/carna/labels"
${dataset_path} = "../dataset/carna/images"
${confog_path} = "./cfg/yolov2-tiny-voc-lab9.cfg"
${pretrain_model_weight} = "./bin/yolov2-tiny-voc.weights"



# initial training
# python flow `
#     --model "${confog_path}" `
#     --load  "${pretrain_model_weight}" `
#     --train `
#     --annotation "${annotation_path}"`
#     --dataset "${dataset_path}" `
#     --gpu 1.0

# continue training
python flow `
    --model "${confog_path}" `
    --load -1 `
    --train `
    --annotation "${annotation_path}" `
    --dataset "${dataset_path}" `
    --lr 1e-5 `
    --gpu 1.0
