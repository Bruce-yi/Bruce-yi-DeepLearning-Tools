# MOT-tools

Tools for evaluating and visualizing results for the Multi Object Tracking

# Requirements

pandas==0.24.2
numpy==1.18.1
opencv_python==3.4.1.15
motmetrics==1.2.0

you can install all the requirements by running
```
$ pip install -r requirement.txt
```

# Evaluation

## check gt file
if you check 'MOT16' or 'MOT17', please make sure 'MOT16-' or 'MOT17-' in your gt file path, then running
```
$ python evaluation/evaluation.py --your_task --isgt --prediction_file your_result_file --data_dir your_gt_data
```
if you use other dataset, please make sure that your dataset in the following structure:
```
 data
   |——————images
   |        └——————train
   |        |        └——————seq1——————gt——————gt.txt
   |        |        └——————seq2——————gt——————gt.txt
   |        └——————test
   └——————labels_with_ids
            └——————train(empty)
```
then, put your prediction txt into a file, like:
```
 folder
   |——————prediction txt1
   └——————prediction txt2
   └——————prediction txt3
```
## evaluation
```
$ python evaluation/evaluation.py --your_task --prediction_file your_result_file --data_dir your_gt_data
```