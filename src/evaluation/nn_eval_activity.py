import numpy as np
import tensorflow as tf


def auc(prob_of_pos, gt):
    '''
        Inputs
            prob_of_pos: np.array 2d, probability of being classified in true class
            gt: np.array 2d, ground truth
            
        Returns
            output: An integer which is area under precision recall curve
            fmeasure: An integer which is the best f1(fmeasure) among different thresholds
            prec: An integer which is the maximum precision obtained from different threshold
            rec: An integer which is the maximum recall obtained from different threshold
    '''
    output_prec = []
    output_rec = []
    
    #here we sort the predicitions for each time step and sort the ground truth
    # with the same index
    idx_sorted_prob = np.argsort(-prob_of_pos.flatten())
    coresponded_gt = gt.flatten()[idx_sorted_prob]
    idx_true_gt = np.sort(np.where(coresponded_gt == 1)[0])
     
            
    # Calculating precision and recall for different thresholds. Also, output_prec is area under
    #the precision recall curve
    for i in range(idx_true_gt.shape[0]):
        output_prec.append(float(i + 1) / float(idx_true_gt[i] + 1))
        output_rec.append(float(i + 1) / float(idx_true_gt.shape[0]))
        
    # Finding the best precision and recall for the best fmeasure among different thresholds
    output_prec = np.asarray(output_prec)
    output_rec = np.asarray(output_rec)
    
    f1_measure = 2 * output_prec * output_rec / (output_prec + output_rec)
    idx_max_fmeasure = np.argmax(f1_measure)
    prec = output_prec[idx_max_fmeasure]
    rec = output_rec[idx_max_fmeasure]
    
    return np.mean(np.asarray(output_prec)) , np.max(f1_measure), prec, rec



def auc_random(gt):
    
    '''
        This function shuffle ground truth and then sort index of label 1.
        Calculate auc, fmeasure, prec and recall on this array.
        
        Inputs
              gt: np.array 2d, ground truth
              
    '''
    
    copy_gt = np.copy(gt)
    output_prec = []
    output_rec = []
    
    flatten_gt = copy_gt.flatten()
    np.random.shuffle (flatten_gt)
    
    #sorting indexes of label 1
    idx_true_gt = np.sort(np.where(flatten_gt == 1)[0])
    
    for i in range(idx_true_gt.shape[0]):    
        output_prec.append(float(i + 1) / float(idx_true_gt[i] + 1))
        output_rec.append(float(i + 1) / float(idx_true_gt.shape[0]))

    output_prec = np.asarray(output_prec)
    output_rec = np.asarray(output_rec)
    
    f1_measure = 2 * output_prec * output_rec / (output_prec + output_rec)
    idx_max_fmeasure = np.argmax(f1_measure)
    prec = output_prec[idx_max_fmeasure]
    rec = output_rec[idx_max_fmeasure]
    
    return np.mean(np.asarray(output_prec)) , np.max(f1_measure), prec, rec

def accuracy(model_out, gt):
    pred = np.argmax(model_out, axis=2)
    truth = np.argmax(gt, axis=2)
    valid = np.sum(gt, axis=2)==1
    
    num_correct = np.logical_and(pred==truth, valid).sum()
    num_incorrect = np.logical_and(pred!=truth, valid).sum()
    
    accuracy = float(num_correct) / (float(num_correct + num_incorrect))
    return accuracy
    

def evaluate_model(model, sess, data, ground_truth):
    
    probability_of_pos, pooled_y, debug_info = sess.run((model.prob_of_pos, model.pooled_y, model.debug_info),
                                  feed_dict={model.x: data, model.y:ground_truth})
    
    acc = accuracy(probability_of_pos, pooled_y)
    
    result = []
    for i in range(pooled_y.shape[2]):  
        if np.max(pooled_y[:,:,i]) > 0:
            result.append(auc(probability_of_pos[:,:,i],
                         (pooled_y[:,:,i]>0.5).astype('int32')))
        
    auc_result = float(sum([i[0] for i in result]))/ float(len(result))
    f1_result = float(sum([i[1] for i in result]))/ float(len(result))

    result = []
    for i in range(pooled_y.shape[2]): 
        if np.max(pooled_y[:,:,i]) > 0:
            result.append(auc_random((pooled_y[:,:,i]>0.5).astype('int32')))
            
    auc_result_random = float(sum([i[0] for i in result]))/ float(len(result))
    f1_result_random = float(sum([i[1] for i in result]))/ float(len(result))
    
    rand_acc = 1.0/float(len(result))
    
    print ("AUC = {:.3f} vs. {:.3f}".format(auc_result, auc_result_random))
    print ("F1 = {:.3f} vs. {:.3f}".format(f1_result, f1_result_random))
    print ("Accuracy = {:.3f} vs. {:.3f}".format(acc, rand_acc))
   
    result = {}
    result['accuracy'] = acc
    result['accuracy_random'] = rand_acc
    result['auc'] = auc_result
    result['f1'] = f1_result
    result['auc_random'] = auc_result_random
    result['f1_random'] = f1_result_random
    
    return result

