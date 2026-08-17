# **Unlearning methods**

* [cao2015](https://ieeexplore.ieee.org/document/7163042)  
  * First paper on the field  
  * removes data traces by converting learning  
  * algorithms into a summation form,   
* [chen2021](https://arxiv.org/abs/2005.02205)  
  * Points out that unlearning often leads to the forgetset having a very different distribution after unlearning  
  * MIA is still possible  
  * These faulty MU methods ensure security (the informatiuon is not in there), but fail to preserve privacy  
  *    
  * Also known as “correlation collapse”??  
* Correlation collapse  
  * Same phenomena pointed by [chen2021](https://arxiv.org/abs/2005.02205)?  
  * I’m describing here as it was descried in [choi2024](https://arxiv.org/pdf/2409.14747)  
  *   
  * inadvertently increase the magnitude of loss excessively, leading to additional data leakage by making certain data points appear special  
  *   
* [nguyen2022](https://arxiv.org/abs/2209.02299)  
  * Review  
  * [https://github.com/tamlhp/awesome-machine-unlearning](https://github.com/tamlhp/awesome-machine-unlearning)   
* [li2023](https://arxiv.org/abs/2305.12320)  
  * Proposes the method Random Relabeling (were they really the first to do this?)  
* [xu2023review](https://dl.acm.org/doi/10.1145/3603620)  
  * Review  
  * Categorize existing unlearning solutions  
* [shaik2024](https://ieeexplore.ieee.org/abstract/document/10750906)  
  * Review  
  * Provides a very clear taxonomy  
  * Also explores attack sophistication and lack of standardization  
  *    
  * Data-centric  
    * Data Deletion  
      * Not efficient?  
    * Mitigating Data Poisoning  
      * Based on existing techniques for dealing with data poisoning  
    * Data Subsampling and Shuffling  
      * good when dealing with large datasets  
      * Particularly important against membership inference  
    * Inverse Data Generation  
      * synthesize datasets that retain the statistical essence of the original data while meticulously excluding sensitive information  
      *   
  * Model-centric  
    *  Transfer Learning  
      * Finetunign without the forget-set  
      * (-) expensive  
    * Dynamic selection  
      * dynamically selects mix-up data augmentation to merge shards requiring retraining, thereby reducing the need for comprehensive retraining  
    * Model Pruning  
      *  selectively removing nonessential parameters.  
    * Knowledge Distillation  
      * Train another model  
    * Model Inversion  
      * aimed at elucidating sensitive information encoded within ML models  
      * reverse-engineer a model’s predictions to infer the characteristics of the underlying training data  
      * 

![][image1]

* [Barez2025](https://arxiv.org/abs/2501.04952)  
  * Open Problems in Machine Unlearning for AI Safety  
  * examine the fundamental constraints  
  * “the entanglement of knowledge within AI models makes it difficult to predict the potential downstream effects of unlearning”  
  * application areas  
    * Safety-Critical Knowledge Management  
    * Mitigating Jailbreaks  
    * Correcting Value Alignment and Improving Corrigibility  
    * Privacy and Legal Compliance  
  * limitations that prevent MU being a comprehensive solution for AI safety  
    *   
* [Geng2025](https://arxiv.org/abs/2503.01854)  
  * Survey for LLMs  
*   
* [Wu2024EraseDiff](https://arxiv.org/html/2401.05779v2)  
  * Or *EDiff*  
  * Modality: image generation  
  * diffusion models  
  * constraint optimization problem, aiming to preserve the utility of the diffusion model on the remaining data and scrub the information associated with forgetting data by deviating the learnable generative process from the ground-truth denoising procedure.  
* [fan2024\_salun](https://arxiv.org/abs/2310.12508)  
  * SalUn  
  * From the lab OPTML  
  * introduce the concept of ‘weight saliency’  
  * directs MU’s attention toward specific model weights  
  * New method called “saliency unlearning (SalUn)”  
  * Novelty: first principled MU approach that can effectively erase the influence of forgetting in both image classification and generation tasks  
  * yields a stability advantage in high-variance random data forgetting  
  * [https://github.com/OPTML-Group/Unlearn-Saliency](https://github.com/OPTML-Group/Unlearn-Saliency)  
  * Uses the same evaluation methodology as in [jia2023](https://proceedings.neurips.cc//paper_files/paper/2023/hash/a204aa68ab4e970e1ceccfb5b5cdc5e4-Abstract-Conference.html). Metrics: unlearning accuracy, membership inference attack on Df using the privacy measure of θu over Df, remaining accuracy, testing accuracy, run-time efficiency  
  * Compares with the following baselines (established unlearning algorithms): Fine-tuning (FT), random labeling (RL), gradient ascent (GA), influence unlearning (IU), ℓ1-sparse,  boundary shrink (BS), and boundary expanding (BE)   
  *    
  * gradient of a forgetting loss, lf(theta, Df), then apply a threshold. Results in a binary mask over the weights.  
  * Theta\_u \= weights under the mask  
  * Theta\_o \= weights outside the mask  
  * plug-and-play capability, allowing it to be applied on top of existing unlearning methods  
  * In the paper, they apply it with the “random labeling” technique: continuated pretraining with the entire data set, but the forget-set has its labels randomly switched  
  *   
  * The threshold can be modified to actually be a soft-threshold. They observed it does not improve results.  
  * *“In practice, we have observed that setting γ to the median of the gradient vector ∇θℓf(θ; Df) |θ=θo is a sufficiently effective choice”*  
  *   
  * Model: ResNet-18 trained on CIFAR-10  
  * ,  
* [golatkar2020](https://arxiv.org/abs/1911.04933)  
  * This approach is also called “Fisher forgetting”; Also called “scrubbing”  
  * Does not require access to the data originally used for training (but requires us to calculate beforehand the hessian $\\nabla ^2 L\_D(w)$)  
  * applicable to both the case where an entire class needs to be forgotten or a particular subset of samples within a class  
  *   
  *   
  * Uses FIM as regularizer to avoid forgetting: after calculating the FIM for Df, compute the optimal noise to destroy information, so that Df can be forgotten while maintaining good accuracy for Dr”  
  *   
  * f: readout function; formalizes the idea of a generic attack; recevies the model w and return information about Df  
  * S: scrubbing function (receives a model and return a model)  
  * h: part of the scrubbing procedure; adjust the weights so that they align with the distribution of weights trained solely on Dr  
  * w′: weights obtained from training a model on 𝐷r  
  *   
  * Formalizes unleaning as minimizing/bounding the amount of additional information f(w) can extract, that could not have been inferred by Dr  
  * Describe their procedure as “Optimal Quadratic Scrubbing Algorithm”  
  *    
  * Calculating the hessian is too expensive, so they use the Levenberg-Marquardt approximation, which coincides with the FIM… but since the FIM is also too large, use a  Kronecker-factorized approximation  
  * If you saved FIM\_d after training, you can compute FIM\_f and FIM\_r just using Df  
  * use the FIM\_f as the covariance of the noise  
  * λ: is a hyper-parameter that trades off forgetting with the increase in error (as a weight for the KL-divergence term)  
  * Analyzes the forgetting based on the histogram of the prediction confidences for different datasets (I’m not sure if they are the first to evaluate this way, but fits well their theoretical analysis):

![][image2]

* Their upper bound is calculated as:  
  ![][image3]  
  *   
* [warnecke2021](https://arxiv.org/abs/2108.11577)  
  * Uses influence functions for estimating the influence of data on learning models  
  *  enables certified unlearning  
  *   
* [izzo2021](https://arxiv.org/abs/2002.10077)  
  * Proposes influence unlearning (IU), aka projective residual update  
  * Requires calculating hat matrix once,  X(X^TX \+ λI)^−1X^T, for the entire dataset  
  * Don’t mention fisher at all, but uses hessian (which is probably approxiumate by FIM)  
  *  time complexity that is linear in the dimension of the deleted data  
  * do not assume that the removed points need to be in any way “similar” to the rest of the data  
  * [https://github.com/zleizzo/datadeletion](https://github.com/zleizzo/datadeletion)   
  *   
  * θo: original model  
  * θu: unlearned model  
  * Wi: influence of one specific dataspoint? Between 0 and 1  
  * θ(w): model being updated during training?  
  * delta w: parameter adjustment required to move from the original model   
  * θo  to the unlearned model θu  
  * θu \= θo \+∆(w)   
  * ​  
  *  Delta w is formally deduced as:  
    ![][image4]  
  * That H^-1 isn’t actually computed? It’ could be approximated by FIM (since the loss function is approximately quadratic, Levenberg-Marquardt approximation works fine), but looking at the code they actually compute \`invhess \= np.linalg.inv(np.matmul(X.T, X) \+ reg \* np.eye(d))\`  
  * H can be computed ahead of time, without needing to know which points will be deleted  
  *   
*   
* [jia2023model](https://arxiv.org/abs/2304.04934)  
  * Proposes the method l1-sparse  
  * sparsity-aware unlearning method  
  * Highly based on IU  
  * From the lab OPTML  
  * Follow up of [izzo2021](https://arxiv.org/abs/2002.10077)  
  * Paradigm of “prune first, then unlearn”  
  *   
  * Adds weight normalization… what else?  
  *    
  * m: binary mask associated with the model  
  * mi \= 0 signifies that the ith parameter is pruned to zero  
  *    
  * Uses the Woodfisher ([singh2020woodfisher](https://arxiv.org/abs/2004.14340)) method to approximate the inverse of the hessian   
  * In the salun paper, they refer to this unlearning method simply as “wfisher”  
*   
*   
  *   
* [Clavera2024](https://upcommons.upc.edu/bitstream/handle/2117/410877/188878.pdf)  
  * Bachelor thesis that reviews FIM-based unlearning  
  * Modality: language💬; Nothing about image generation  
* [Liu2025](https://arxiv.org/abs/2502.15910)  
  * Modality: multimodal 💬🖼️  
  * Propose Modality Aware Neuron Unlearning (MANU)  
  * selectively clip neurons based on their relative importance to the targeted forget data, curated for different modalities  
  * important neuron selection  
    * identifies and collects the most influential neurons across modalities relative to the targeted forget knowledge  
    * relative importance of neurons in the language and vision MLP layers for both the forget set Df and retain set Dr  
    * Saliency \= difference in activation magnitudes between modalities relative to an arbitrary dataset  
    * frequency importance (Ifreq) \= quantify how often a neuron’s activation significantly deviates from zero; helps distinguish consistently engaged neurons from those that activate only sporadically; How is this used…?  
    * Separate by modality  
    *   
    * determine the pruned neurons based on the calculated importance  
    * Ratio importance(Df) / Importance(Dr)  
    *  the top α% of neurons are selected  
    *   
  * selective pruning  
    * pruning those selected neurons  
    * Finetuninig? Or just removed?  
* [Huo2025](https://arxiv.org/abs/2502.11051)  
  * Modality: multimodal💬🖼️  
  * develop MMUnlearner  
  * geometry-constrained gradient descent method  
  * Selective Updating  
    * “the conflicting directions of the Forget loss and the Retain loss make the unlearning process unstable” \-\> these guys didn’t read Munba…  
    * updates the weights of MLLMs with a weight saliency map jointly restricted by the remaining concepts and textual knowledge during unlearning  
    * Selection mask \= m \= saliency\_forget / saliency\_retain \> threshold  
    * Where Saliency is calculated with gradient

    ![][image5]

*    
*    
*    
* [Tarun2023](https://arxiv.org/pdf/2210.08196)  
  * Based on knowledge distillation  
  * ‼️important read‼️  
* [Gandikota2023](https://arxiv.org/abs/2303.07345)  
  * Erased Stable Diffusion (ESD)  
  *  propose an energy-based method tailored to classifier-free guidance mechanisms for erasing  
  * concepts in text-to-image diffusion models  
  * ‼️important read‼️  
*   
* [Heng2023](https://arxiv.org/abs/2305.10120)  
  * Selective Amnesia (SA)  
  * continual learning framework to erase concepts across various types of generative models.  
  * leverage Elastic Weight Consolidation and Generative Replay to forget target concepts while maintaining overall model performance  
  * Performs concept overwriting ↔️  
* [Zhang2023\_fmn](https://arxiv.org/abs/2303.17591)  
  * Forget-me-not (FMN)  
  * Works for stable diffusion  
  * (+) Fast 🚀  
  * Parameter efficient?  
  * Only finetunes the text encoder?  
  * [https://github.com/SHI-Labs/Forget-Me-Not](https://github.com/SHI-Labs/Forget-Me-Not)   
* [kumari2023](https://arxiv.org/abs/2303.13516)  
  * Modality: vision🖼️  
  * AC (ablating concepts), sometimes said Concept Ablation (CA)  
  * Works for stable diffusion  
  * Performs concept overwrite ↔️  
  * Pretty much the same logic as FADE  
* [li2024SEOT](https://github.com/sen-mao/SuppressEOT)  
  * Or *SuppresedEOT*  
  * do not rely on fine-tuning  
* [Gandikota2023UCE](https://arxiv.org/abs/2308.14761)  
  * UCE (unified concept editing)  
  * Works for stable diffusion  
  * (+) Fast 🚀  
  * Parameter efficient?  
  * More or less performs concept overwrite ↔️… map target concepts to surrogate sae retain concepts…  
  * modifies cross-attention in the U-Net (Wk and Wv)  
  * builds upon previous model editing work, generalizing the TIME and MEMIT  
  * [https://github.com/rohitgandikota/unified-concept-editing](https://github.com/rohitgandikota/unified-concept-editing)   
  *    
  * Metrics: CLIP, LPIPS, FID  
  *    
  * ci: source embedding (derived from the tokens of the source prompt)  
  * ci∗: destination embeddings (from the embeddings of the corresponding tokens in destination prompt). Come from the “guide\_concepts” hyperparam?  
  * cj: concepts to be preserved  
  * Updates only weights related to forget concepts, while minimizing changes to the set of weights related to retain concepts  
  * Update is regularized by a parameter lambda, L2 of W\_old \- W\_new  
  * find weights so that the output for each of the forget inputs inputs c\_i maps to target values v\_i^\* instead of the original value v\_i  
    ![][image6]  
  * Debiasing mode  
    * we want the model to generate the concept with evenly distributed attributes a1, a2, …, ap  
    * achieved by adjusting the magnitude of vi along the directions of va1 , va2 , ..., vap  
    * As debiasing one concept can affect others, we use an iterative approach  
      ![][image7]  
* [Gong2024RECE](https://arxiv.org/abs/2407.12383)  
  * RECE  
  * Builds uppon UCE  
  * closed-form solution to derive new target embeddings  
* [Wu2024\_scissorhands](https://arxiv.org/abs/2401.06187)  
  * Or *SHS*  
  * [https://link.springer.com/chapter/10.1007/978-3-031-72970-6\_21](https://link.springer.com/chapter/10.1007/978-3-031-72970-6_21)   
* [Wu2024\_munba](https://arxiv.org/pdf/2411.15537)  
  * MUNBa  
  * Naive approaches to balance forgetting and preserving leads to gradient conflicts  
  * reformulate MU as a two-player cooperative game, where the two players, namely, the forgetting player and the preservation player, contribute via their gradient proposals to maximize their overall gain  
  * Nash bargaining theory  
  * Strongly inspired by [this](https://arxiv.org/pdf/2202.01017) paper; they have a [github](https://github.com/AvivNavon/nash-mtl)  
  * **Some notes on Multi criteria optimization**  
    * A candidate solution A dominates another B, $c(\\bold A) \\prec c(\\bold B)$, if A is equally good than B in every criteria, and its better in at least one  
    * Paretto optimal candidate: a candidate that is not dominated by any other candidate  
    * Paretto set: set of all paretto optimal candidates  
    * Pareto front: line/plane formed by pareto set points; it is common that optimziation algorithms work work with more than one front, such that the elements in Front2 are only dominated by points in Front1, and so on  
  *   
  * **Algorithm**  
    * \\tilde g: joint direction for updating the model  
    * u\_r  and u\_f: utility; calculating by projecting $\\tilde g$ in the direction of each gradient?  
    * a\_r and a\_f: scalars that scale the loss for each objective; Calculated like this to maximize the resulting gradient:  
      ![][image8]  
    *    
    * For each batch in the gradient descend loop, compute the gradient for each dataset, put in a 1x2 vector G  
    * Multiply G with itself to obtain g1, g2, g3 g4, and alpha  
    * Calculate a\_r and a\_f  
    * Multiply each gradient by a\_r and a\_f and sum it along the parameter dimension  
    * Use this scaled gradient in your gradient descent parameter update  
  *    
  *   
  *   
  * **Setup for classification**  
    * randomly selected 10% of the data  
    * Tested model: ResNet  
    * Tested datasets: CIFAR-10, SVHN, Celeb-HQ-307  
    * Metrics: AccDf (↓), AccDt (↑), AccDr (↑), MIA(↑), Avg. Gap  
  * **Setup for embedding**  
    * Tested model: CLIP with ViT-B/32  
    * Tested datasets: ImageNet-1K, Oxford Pets  
  * **Setup for image generation \- Concept-wise forgetting**  
    * mitigate the generation of NSFW   
    * Pretty much the same setup as Selective Amnesia  
    * Tested model: SD v1.4  
    * Tested dataset: inappropriate images generated with SD v1.4 (we generate ∼400 images with the prompts cf \={‘nudity’, ‘naked’, ‘erotic’, ‘sexual’} as Df; generate ∼400 images with the prompt cr \={‘a person wearing clothes’} as Dr; evaluate on 1K generated images with prompts cf  and 4703 generated images with I2P)  
    *   
    * Metrics: Quantity of nudity content detected using the NudeNet classifier ( threshold of 0.6 for identifying instances of nudity), FID  (for image quality?), Attack success Rate (for membership inference; Using UnlearnDiffAtk), CLIP score  
    * FID and CLIP are measured over the images generated by the scrubbed models with COCO-30K prompts  
    * For ASKR, prepended prompt perturbations by N \= 5 tokens, sample 50 diffusion time steps, and perform attack running for 40 iterations with a learning rate of 0.01 at each step  
    *   
    * Compared techniques: Erased Stable Diffusion (ESD), Selective Amnesia (SA), SalUn, scciorhands (SH),  MUNBa  
    * Comparison results:  
      ![][image9]  
      ![][image10]  
      ![][image11]  
  * **Setup for image generation \- Class-wise forgetting**  
    * The forgetting class cf is specified using the prompt ‘animage of \[cf \]’  
    * The classes are chosen to be from imagenette  
    * Pretty much same setup as salun  
    * Tested model: SD v1.4  
    * Tested datasets: Imagenette  
    * Metrics: FID, UnlearnAccuracy  
    * Compared techniques: Erased Stable Diffusion (ESD), Selective Amnesia (SA), SalUn, scciorhands (SH),  MUNBa  
    * Comparison results:  
      ![][image12]  
      ![][image13]  
        
        
    * I’m very confused about how they compare thse metrics: salun reports class-wise forgetting on Imagenette achieving FID 1.22, with ESD achieving 1.49. The values reported by munba are not only very different in scale, but ESD was considerably better than SalUn  
* [Lyu2023SPM](https://arxiv.org/abs/2312.16145)  
  * Semi-Permeable Membrane (SPM)  
  * Parameter efficient?  
  * lightweight solution for multi-concept erasure by introducing a regulated erasing signal within intermediate layers, although it may struggle with partial unlearning (traces of the target concept remain). Uses Lora ⏩?  
  * Performs concept overwriting ↔️???  
* **ConceptPrune**  
  * ?  
  * (+) Fast 🚀  
  * Parameter efficient?  
*   
* [Varshney2025](https://arxiv.org/pdf/2502.04260)  
  * decouples the model parameters with gradient ascent, ensuring that forget samples are OOD for unlearned model with theoretical guarantee  
  * Image-to-Image  
  * also propose a data poisoning attack  
  * (ϵ, δ)-unlearning guarantee??  
* [Sun2025](https://arxiv.org/abs/2505.02884)  
  * Modality: language💬 (specifically QnA?)  
  * Motivation: existing methods often rely on obfuscation by injecting incorrect or irrelevant information to suppress knowledge  
  * formally distinguish unlearning from obfuscation  
  * introduce a probing-based evaluation framework  
  *   
  *   
  * method DF-MCQ, a novel unlearning method that flattens the model predictive distribution over automatically generated multiple-choice questions using KL-divergence  
  * Test dataset: Wikipedia Person Unlearning (WPU)  
* [Ma2025](https://arxiv.org/abs/2506.10946)  
  * Modality: language💬  
  * GUARD  
  * Motivation: mitigates unintended losses in retention  
  *   
  * Before unlearning, quantifies the alignment between the forget and retain sets  
  * weights to samples, inversely proportional to their alignment  
  * degree of adjustment modulated by a temperature parameter τ  
  * Alignment calculated by dot product of gradients in retain and forget sets?  
  *   
  * Evaluated on: TOFU benchmark  
* [Shi2025CKU](https://arxiv.org/abs/2505.18588)  
  * Constrained Knowledge Unlearning (CKU)  
  * Focus on unlearning/finetuning for the task of Safety Alignment  
  * Very similar to SalUn  
  *   
  * Identify a subset U of neurons associated with retain knowledge  
  * Neuron Locking Rate (NLR): percentage of frozen neurons; Recommends 80%  
  * During the unlearning process (using any method, but they tested with gradient ascent), CKU prunes (or fully freeze?) the gradients of neurons in U  
  *    
  * Tested models: Llama2-7BChat  
    ![][image14]  
* ItD  
  * [https://www.semanticscholar.org/reader/646dd2262ac7408df7ab2d632be55cbda5a8975b](https://www.semanticscholar.org/reader/646dd2262ac7408df7ab2d632be55cbda5a8975b)  
* [https://www.semanticscholar.org/reader/a2d5e1bfb8ed775921484707d30173ad7c54ce9c](https://www.semanticscholar.org/reader/a2d5e1bfb8ed775921484707d30173ad7c54ce9c)  
  * Uses LoRA ⏩  
  * final layers of the text encoders  
* [Cywinski2025](https://export.arxiv.org/pdf/2501.18052v3)  
  * SAeUron  
  * Interpretable Concept Unlearning in Diffusion Models with Sparse Autoencoders  
  * can remove multiple concepts simultaneously  
  * [https://github.com/cywinski/SAeUron](https://github.com/cywinski/SAeUron)  
  *   
  * Assumes (and partially proves) that SAEs,trained in an unsupervised manner on activations from multiple denoising timesteps of the diffusion model, capture sparse and interpretable features corresponding to specific concepts  
  * Assume well-disentangled and interpretable  
  * They trained a single SAE on activations from multiple denoising steps of a standard, non-distilled Stable Diffusion model  
  *   
  * Hyperparams: number of blocked features τc and negative multiplier γc.  
  * Step 0: train SAE  
  * Step 1  
    * Given a trained SAE, identify which SAE features will be targeted for unlearning a specific concept c  
    * features with high scores exhibit strong activation for concept c while remaining weakly activated for all other concepts  
    * we filter out features based on their activation frequency to exclude dead features and those activating too frequently  
  * Step 2:  
    * during the inference of the diffusion model, we encode the original activations with SAE, ablate the selected features to remove the targeted concept associated with them, and decode them back  
    * apply for each timestep t  
    * Identified features are scaled with a negative multiplier  
    * Removing frogs during inference:

    ![][image15]

  *   
  * Evaluation  
    * unlearn canvas  
    * I2P \+ nudenet; 4703 inappropriate prompts; Sd 1.4; calculate FID and CLIPScore; on 30k prompts from the COCO validation set  
    * sequential unlearning?  
    * Parallel unlearning; unlearn 49 out of 50 styles present in the UnlearnCanvas  
    *  tune hyperparameters on the validation set  
    * DiffAtk method (Zhang et al., 2025), optimizing a 5-token prefix for 40 iterations with a learning rate of 0.01  
  * DO FEATURES RELATE TO CONCEPTS?  
    * visualize feature activations on corresponding image patches  
    * style-related features strongly activate on patches with characteristic style patterns  
    * object-related features activate only on the targeted object  
      ![][image16]  
* [Thakral2025fade](https://arxiv.org/pdf/2503.19783)  
  * FADE (Fine grained Attenuation for Diffusion Erasure)  
  * LoRA-based ⏩  
  * Mmentions interference under the name of collateral forgetting “adjacency problem”  
  * Design a method to prevent that  
  * Considerations about interference  
  *   
  * “Despite progress, achieving adjacency-aware erasure while maintaining locality remains a significant challenge. Current unlearning methods often struggle with fine-grained concept forgetting, inadvertently affecting the semantic neighborhood of the target concept”  
  * Methods often lack finegrained control, inadvertently affecting semantically similar classes when erasing a target concept  
  * semantically similar concepts are disproportionately affected during erasure  
  * ![][image17]  
  * notation  
    *  Let D \= {d1, d2, . . . , dN } represent a dataset where each data point di is associated with a subset of concepts Cdi ⊆ C  
    * Ctar \= concept to be forgotten  
    * A(ctar) ⊆ C denote the adjacency set, containing concepts closely related to ctar.  
    *    
    * organizes model knowledge into three subsets: the Unlearning Set Du, the Adjacency Set Da, and the Retain Set Dr.  
    * Du ∪ Da ∪ Dr ⊆ D, with Du ∩ Da ∩ Dr \= ∅  
  *   
  * How it works: Carefully constructed set of semantically related classes that should remain unaffected by unlearning  
  * Concept Neighborhood  
    * systematically identifies semantically proximal classes to ctar   
    * semantic similarity  
    * Generate iamges, compute embeddings for each image, cosine similarity between their mean embeddings (defined L(concept1, concept2)  
    * Form Da by select the top-K concepts with the highest similarity  
  * Mesh Modules, ? Uses LoRA to selectively updates only a subset of  
  * model parameters. Expungement, Adjacency, and Guidance loss components?  
  *    
  * Erasing-Retention Balance Score (ERB)  
    * Proposed new metric  
    * quantifies both forgetting and adjacency retention  
    * A \= classification accuracy of a pre-trained ResNet-50   
      ![][image18]  
  * Tested methods:  Erased Stable Diffusion (ESD) \[9\], Concept Ablation (CA) \[17\], Forget-Me-Not (FMN) \[33\], Semi-Permeable Membrane (SPM) \[18\], and Receler \[15\]  
  * Tested model:  SD v1.4  
  * Finegrained datasets  
    * Stanford Dogs \[16\], Oxford Flowers \[20\], Caltech UCSD Birds (CUB) \[32\], and ImageNet-1k \[24\]  
    *  three target classes per fine-grained dataset and four target classes in ImageNet-1k.  
    *    
    * select three target classes for each dataset and define their adjacency sets using Concept Neighborhood with K \= 5  
  * Coursegrained Datasets  
    * standard evaluation protocols \[9, 15\] for the Imagenette \[13\] and I2P \[25\] datasets  
    * For I2P, we use NudeNet \[2\] to count nudity classes and FID \[11\] to measure visual fidelity between the original and unlearned models  
  * User Study  
    * 40 participants  
    * Each participant evaluated 81 images  
* [Tinaz2026](https://arxiv.org/pdf/2504.15473)  
  *  leverage the SAE framework to probe the inner workings of a popular text-to-image diffusion model, and uncover a variety of human-interpretable concepts in its activations  
* [Thakral2025duge](https://arxiv.org/pdf/2503.13769)  
  * Decremental Unlearning without Generalization Erosion (DUGE)  
  * Continual unlearning 🔁  
  * three losses: a cross-attention loss that steers the focus towards images devoid of the target concept; a prior-preservation loss that safeguards knowledge related to non-target concepts; and a regularization loss that prevents the model from suffering from generalization erosion.

  ## Parameter efficient, sparse

* [Huang2024Receler](https://arxiv.org/html/2311.17717)  
  * Reliable Concept Erasing via Lightweight Erasers (Receler)  
  * Modality: vision🖼️ (Text-to-Image Diffusion Models)  
  * What is updated: Finetunes the cross-attention layer within the diffusion U-Net; Adapter-based PEFT, but do not use LoRA  
  * What can be unlearned: Only concept erasing?  
  * concept-localized regularization and adversarial prompt learning scheme  
  * desirable properties: locality (ability to preserve the model generalization in synthesizing content not associated with the target concept) and robustness (effectively remove the target concept)  
  * Reports modifying only a very small percentage of weights, \<1%  
  *   
  * Data free?  
  * concept-localized regularization  
    * leveraging the spatial information associated with the target concept’s text tokens to regularize the eraser outputs?  
    * thresholding the attention maps when predicting text tokens corresponding to the forget concept?  
  * Adversarial Prompt Learning  
    * optimizes the continuous soft prompts  by encouraging such learned prompts to imitate the malicious prompts  
  *    
  * Compared with methods: FMN, Ablating, ESD, UCE  
  * Model: SD v1.4  
  * Tasks: Forget object from CIFAR-10, nudity (with prompts from I2P dataset), style forgetting (but do not report quantitative results)  
  * Metrics: Accuracies, Nudity-erased ratio, CLIP, FID  
  * CLIP and FID are measured on COCO-30K prompts  
  * Adversarial test with P4D and Ring-A-Bell  
    ![][image19]  
* [Lu2024MACE](https://openaccess.thecvf.com/content/CVPR2024/html/Lu_MACE_Mass_Concept_Erasure_in_Diffusion_Models_CVPR_2024_paper.html)  
  * Mass Concept Erasure (MACE)  
  * (+) Fast 🚀  
  * Can remove  up to 100 concepts in one finetunnign session (just by having loras?)  
  * closed-form cross-attention refinement along with LoRA finetuning  
  * [https://github.com/Shilin-LU/MACE](https://github.com/Shilin-LU/MACE)  
  * specifically for Diffusion Models  
  * uses lora ⏩  
  * Performs concept overwriting ↔️ ???  
  *   
  * separate LoRA modules for each concept  
  * concept-focal importance sampling…?  
    * we opt not to sample the timestep t from a uniform distribution when training LoRA  
    * sampling distribution that assigns greater probability to smaller values of t  
    * increasing the speciﬁcity  
    * Focus on the beginning of the generation trajectory  
  * Closed-Form Cross-Attention Reﬁnement  
    * encourage the model to refrain from embedding residual information of the target phrase into other words  
    * The Wk attention matrix is finetuned  such that the target word is mapped to the overwriting word  
    *   
  * loss function that integrate multiple LoRAs  
  * Grounded-SAM? Training data is enriched with segmentation masks?  
  * Proper many-lora merging  
    * naı̈ve weighted sum leads to interference among the modules  
    *   
  * Each LoRA module is trained for 50 gradient update steps.  
  * Evaluation  
    * augment the input target concept using prompts generated by the GPT-4  
    *   
  *   
*   
* [zhang2023](https://arxiv.org/abs/2306.14870)  
  * Unlearning by subtracting LoRa adapters ⏩  
  * Also tested (IA)3  
  * The paper is actuaolly about LoRa “arithmetrics”  
  *  compose LoRa modules through linear arithmetic operations  
  *  requires no additional training  
  * [https://github.com/hkust-nlp/PEM\_composition](https://github.com/hkust-nlp/PEM_composition)  
  * [https://neurips.cc/virtual/2023/poster/72784](https://neurips.cc/virtual/2023/poster/72784)  
  * Published at NeurIPS (IF \~30)  
  * 97 citations  
  *    
  * composition of skills through an analogy operation, similar to the well-known word embedding equation “queen \= king \- man \+ woman”   
  * achieving significant gains using a new PEM derived from arithmetic operations of existing ones  
  * θ1 ⊖ θ2 ⊕ θ3 for transferring a model across domains  
  * Addition  
    * pairing the arguments at corresponding positions  
    * adding them component-wise  
  * Negation  
    * cannot be reduced to simply negating all parameters of PEMs  
    * focus on the modification that the PEMs apply to the hidden states h  
  *  Distribution Generalization  
    * Datasets: MNLI, RTE, CoLA, SST2, MRPC, QNLI, QQP, and STS-B  
    * RoBERTa-base as the base mode  
  * Multi-Tasking  
  * Unlearning  
    * Base model: GPT-2 large  
    * LoRa trained on toxic comments of Civil Comments dataset  
  * Domain Transfer  
  *    
  * Parameter lambda?  
  *   
  *   
* [Hu2024](https://arxiv.org/abs/2308.08090)  
  *  [https://github.com/HITsz-TMG/Ext-Sub](https://github.com/HITsz-TMG/Ext-Sub)  
  * Published at AAAI conference (IF 9.25), March 2024  
  * 5 citation, 17 commits, 11 starts  
  * through the integration of \`\`expert'' PEM and \`\`anti-expert'' PEM  
  * Rather than merely negating the parameters, our approach involves extracting and eliminating solely the deficiency capability within anti-expert PEM  
* [Ding2024](https://arxiv.org/pdf/2412.00383)  
  * Method LLMEraser  
  * “privacy and security concerns, as models may inadvertently retain and disseminate sensitive or undesirable information”  
  * using influence functions  
* [Qin2024](https://arxiv.org/pdf/2411.08443)  
  * Image classification  
  * residual feature alignment: ? ensuring that the lora branch otuputs zero for the retain set?  
  * residual feature alignment using LoRA ⏩  
  * teacher-student framework  
  * We decompose the model’s features into pre-trained features and residual features, obtained from the pre-trained branch and the bypass branch (lora)  
  *   
* [Gao2024](https://arxiv.org/pdf/2407.10223)  
* [Wang2024](https://arxiv.org/pdf/2403.03536)  
  * Method E2URec  
  * LLM for recommendation  
  * [https://github.com/justarter/E2URec](https://github.com/justarter/E2URec)   
  * 9 citations  
  * Published at Frontiers Comput. Sci. (IF 3.21), march 2024  
  *    
  * employing a teacher-student framework  
* [Zhao2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Zhao_Continual_Forgetting_for_Pre-trained_Vision_Models_CVPR_2024_paper.pdf)  
  * Method Gs-LoRa  
  * ⏩  
  * CVPR  
  * face recognition, object detection and image classification  
  *   
  * [https://github.com/bjzhb666/GS-LoRA](https://github.com/bjzhb666/GS-LoRA)  
* [Premptis2025](https://arxiv.org/abs/2503.02443)  
  * Modality: Language💬  
  * LoRA ⏩  
  * employ data chunking, splitting forget data into disjoint partitions and merging them with cyclically sampled retain samples at a pre-defined ratio  
* [Yang2025](https://arxiv.org/abs/2502.19207)  
  * Introduces KLUE  
  * Method KLUE  
  * Modality: language (specifically QnA) 💬  
  * identifies knowledge neurons using an explainability method and updates only those neurons using selected unforgotten samples  
  * Sparse, updates only a few neurons  
  * updates only knowledge-related neurons  
  * identifies knowledge neurons using an explainability method and updates only those neurons  
  * Motivated by existance of entanglements (or “Interconnectedness of Knowledge”) and revival of knowledge  
  *   
  * superficial unlearning: phenomenon where an unlearning method either fails to erase the interconnected knowledge it should remove or unintentionally erases irrelevant \[to the forgetting task\] knowledge  
  *   
  * FaithUn  
    * new benchmark  
  * Parameter selection  
    * Find relevant neurons to the forget task by using DeepLIFT, then remove neurons that were found relevant (by the same method) in a dataset of randomly matched questions-and-answers  
* [Wang2025SSPU](https://arxiv.org/abs/2505.24428)  
  * Modality: language💬  
  * propose SAE-Guided Subspace Projection Unlearning (SSPU)  
  * targeted updates in the model's parameter space  
  *    
  * Feature Selection: extract SAE activations on forget and retain examples, compute activation scores, and select the top- and bottom-ranked latent dimensions.  
  * Subspace Construction: collect decoder vectors for the selected features and perform QR decomposition to obtain orthonormal bases for the relevant and irrelevant subspaces.  
  * Sparse AutoEncoder Guided Subspace Projection Unlearning: at each iteration, draw forget and retain batches, extract updated and reference activations, project a random vector into the irrelevant subspace to form a control signal, apply unlearning and retention losses, and restrict weight updates to the relevant subspace.  
    ![][image20]  
* LoRAShield  
  * [https://www.semanticscholar.org/reader/6df64e4f5ba8443af87dc16cc37fec45b8c27207](https://www.semanticscholar.org/reader/6df64e4f5ba8443af87dc16cc37fec45b8c27207)  
  * Specifically focused on being robust against adversarial attacks  
*   
* [Cai2025Slug](https://arxiv.org/html/2407.11867v3)  
  * Single Layer Unlearning Gradient (SLUG)  
  * updating a single critical layer using a one-time gradient computation  
  * Tested models: CLIP (ranging from ViT-B-32 to EVA01-g-14), Stable Diffusion (SDv1.5 and SDv2.1), and vision-language models (LLaVA-v1.5-7B)  
  * [https://github.com/CSIPlab/SLUG](https://github.com/CSIPlab/SLUG)  
  * Loss functions for vision-language alignment.  
    * For the retain set, we use the original contrastive loss  
    * For the forget set, we use the cosine embedding loss  
  * Layer identification  
    * uses layer importance and gradient alignment metrics to identify the optimal layer  
    *   
    * importance of a layer l \= ℓ2 norm of the forget loss gradients / the ℓ2 norm of the layer l parameters θl  
    * Alignment  of a layer l \= cosine between forget gradient and retain gradient  
    * To balance both objectives, we search for a Pareto-optimal set across all layer  
  * Optimized update  
    * Dont compute gradient every epoch to save time? Wtf?  
    * calculating the gradient only once for the initial model and updating the parameters θl of any layer l in a weight-arithmetic fashion  
    *    
    *   
  * evaluation  
    * UnlearnCanvas  
    * For CLIP:zero-shot classification  
    * For SD  
      * update the text encoder  
      * UnlearnCanvas  
    * For VLMs: vision encoder  
    *    
    * CelebA dataset (Liu et al., 2015), sampling 100 frequently appearing celebrities from LAION-400M  
    * The utility of post-unlearning models were evaluated with ImageNet  
    * dataset.   
    * Hyperparameters: binary search to determine the step size λ; on a small validation subset  
  * [li2025sculpting](https://arxiv.org/abs/2504.09039)  
    * Sculpting Memory  
    * Multi concept  
    * Performs concept overwriting ↔️ (which they call "substituting with a corresponding superclass or opposing class")

  ## Timestep selection

* Key Step Concept Unlearning (KSCU)  
  * [https://arxiv.org/abs/2507.06526](https://arxiv.org/abs/2507.06526)  
  *   
  * 

  ## Density-based unlearning

  Density aware algorithms have been successful in other applications ([Ghosh2019](https://arxiv.org/pdf/1904.03911), [yamada2011](https://arxiv.org/abs/1106.4729)), but have been little explored to unlearning


* [kong2022](https://arxiv.org/abs/2206.14439v1)  
  * Done in an GAN  
  * Density-ratio-based  
  * P hat \= density ratio between pre-trained and re-trained models  
  *   
  * P hat epsilon \= learned density ratio estimator (DRE) between Df and Do. Derive a DRE based on variational divergence minimization (this seems very GAN-specific…?). KL-based loss function  
  * Drawing samples from the approximated model is done in two steps: first draw samples from phat, and then perform rejection sampling according to ρ\_hat\_epsilon  
  * they also designed a statistical test mechanism through likelihood ratio and ASC statistic, to determine whether data has been deleted.  
  * Rejection-based  
  * feature-density  
* [choi2024](https://arxiv.org/pdf/2409.14747)  
  * Method Distribution-Level Feature Distancing (DLFD)  
  * Specially interested in solving the problem of “correlation collapse”  
  * Hypothezises that correlation collapse not only allow MIA, but hurt maintaining the quality in non-forget tasks  
  * Data-centric  
  * Feature-density  
  * Does not leverage any sparsity approach  
  * [https://github.com/Dasol-Choi/DLFD](https://github.com/Dasol-Choi/DLFD)   
  * Highly based on their previous work [choi2023](https://arxiv.org/abs/2311.02240)  
  *    
  * synthesizes data samples by optimizing the feature distribution to be distinctly different from that of forget samples  
  * shifts the feature distribution of the retain images away from the distribution of the forget images, by leveraging the Optimal Transport (OT)  
  * feature vector w ∈ W corresponding to an image x  
  * W\_task ⊂ W: set of features/manifold relevant for a task  
  * W\_identity ⊂ W: set of features relevant for identifying someone  
  * Both intersect, aka are “entangled”  
  * DLFD preserves the structure of Wtask while modifying Widentity  
  * considers the entire distribution of the data  
  * Step 1 \- Feature Distribution Optimization  
    * shifts the retain data distribution (µ) away from the forget data distribution  
    * Uses OT  
    * employ a differentiable Sinkhorn method (used to solve the optimal transport problem)  
    * Calculates a transport plan T such that: T^{\\lambda} \= \\arg\\min\_{T \\in \\Pi(\\mu, \\nu)} \\langle T, C \\rangle \- \\frac{1}{\\lambda} \\sum\_{i=1}^{n} \\sum\_{j=1}^{n} T\_{ij} \\log T\_{ij}  
      ![][image21]  
  * Step 2 \- Classification Loss Preservation  
    * Use a classification loss guiding the perturbation process to address correlation collapse.  
    * dynamically adjusting the importance of the classification loss throughout the training process  
    * Hyperparameter lambda: balance the trade-off between maximizing the OT loss and preserving the classification accuracy  
    * lOT: OT loss between the retain and forget data distributions  
    * lCE: classification loss: x\_i^\* \\leftarrow x\_i \+ \\alpha \\cdot \\text{sign} \\left( \\nabla\_{x\_i} \[l\_{OT} \- \\lambda \\cdot l\_{CE}\] \\right)  
      ![][image22]  
  * Step 3 \- Dynamic Forgetting Strategy  
    * Adaptive approach designed to optimize the forgetting process by continuously monitoring the forgetting score during training  
    * When the forgetting score drops below a predefined threshold (model has sufficiently forgotten Df), increases lambda (shifts its focus from OT to the classification loss)  
    * ensures that the model’s original task performance remains stable.  
  * Used datasets  
    * Age Estimation: MUFAC  
    * Emotion Recognition: RAF-DB  
    * Multi-Attribute Classification: MUCAC  
  * Used models  
    * ResNet  
    * DenseNet  
    * EfficientNet  
* [Pandas2024](https://arxiv.org/pdf/2312.14895)  
  * encoding the representation of unwanted features in the latent space (unwanted \= images that received negative feedback from users)  
  * During inference, compute similarity metrics with newly sampled latent vectors and the previously identified regions  
  * Apply a threshold to exclude undesirable samples from the output  
  * [https://github.com/Subhodip123/weak-unlearning-gan](https://github.com/Subhodip123/weak-unlearning-gan)   
  *   
  * Reject generations, but don’t erase the information from the network  
  * Latent density


  

  Adversarial approaches may implicitly regularize weight update in heigh density regions. For example in [https://arxiv.org/pdf/2411.15537](https://arxiv.org/pdf/2411.15537), where the gradient is combined by the proposals of the forgetting player and the preservation player


  However, such approaches require several gradient evaluations for each datapoint; Density-based approaches may offer a “zero shot” solution, with a density estimation calculated ahead of time for the entire D, then used to calculate the ideal update with one single gradient calculation


  

  ## Distilation-based

* [Kim2023](https://arxiv.org/abs/2307.05977)  
  * Safe self-distillation diffusion (SDD)  
  * finetunes the model by enforcing the noise estimate conditioned  
  * on a target concept to align with the unconditional one  
  *   
* [chen2025scoreforgettingdistillation](https://arxiv.org/abs/2409.11219)  
  * Score Forgetting Distillation (SFD)  
  * by aligning the conditional scores of “unsafe” classes or concepts with those of “safe” ones  
  * incorporates a score-based MU loss into the score distillation objective (serves as a regularization term that preserves desired generation capabilities)  
  * Building on recent advancements in data-free diffusion distillation for one-step generation  
  * “ existing methods are all based on standard multi-step diffusion models, making them not directly compatible with more efficient one-step diffusion models distilled using score distillation methods.”  
  * [https://github.com/tqch/score-forgetting-distillation](https://github.com/tqch/score-forgetting-distillation)  
  * Seems to be strongly based on [this paper](https://arxiv.org/abs/2406.01561v1) (have one author in common)  
  * demonstrated through both class and concept forgetting  
  *   
  *   
  * optimizing two learnable modules—a generator network and a score network  
  * guided by the frozen pre-trained model itself  
  * distillation \= concurrently optimize the score-matching loss and the forgetting loss  
  * first trains the approximate score estimator s\_ψ to mimic the score of the generator g\_θ at different time points t of the forward diffusion process, and then uses both the pre-trained score estimator and the fake score estimator across these time points to instruct the generator itself  
  *   
    ![][image23]  
  * Score network  
    * trained to optimize the score associated with the generator by minimizing a score distillation loss, which aims to match the conditional scores of the class to forget and the classes to remember with those of the pre-trained model  
  * Generator network  
    * learns to produce examples that are “indistinguishable” by the pretrained score network and fake score network in terms of score predictions, utilizing a model-based cross-class score distillation loss.  
  *    
  * alternating update strategy between θ and  and ψ

![][image24]

* Solving this problem directly is challenging, so we initially relax the constraint specified by Lsfd in the above equation by integrating it into the distillation objective as an additional MU regularization term:

![][image25]

* Class-forgetting setup  
  * Datasets: CIFAR-10 and STL-10  
    * Models: DDPM and EDM, Stable Diffusion  
    * Metrics: Unlearning Accuracy (UA), Fréchet Inception Distance (FID), Inception Score (IS), Precision and Recall, speed  
    * For class forgetting in class-conditional diffusion models, our goal is to unlearn a specific class by overriding it with another class while minimizing any negative impact on the remaining classes  
    * Co \= class used to override  
  * Concept-forgetting setup  
    * goal is to unlearn the concepts associated with specific keywords, such as “Brad Pitt,” by substituting them with more generic terms like “a middle aged man,”  
    * Datasets: Celebrity and NSFT  
* [Kim2024](https://arxiv.org/abs/2402.17323)  
  * stable diffusion deep generative replay (SDDGR)  
  * iterative refinement strategy to produce high-quality images encompassing old classes  
  * adopt an L2 knowledge distillation technique to improve the retention of prior knowledge in synthetic images.   
* [Kurmanji2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/062d711fb777322e2152435459e6e9d9-Abstract-Conference.html)  
  * Method SCRUB  
  * Uses a teacher-student distillation framework to maximize loss on the forget set while minimizing it on the retain set.  
  * [https://scholar.google.com.hk/scholar?oi=bibs\&hl=en\&cites=3914196277753196289\&as\_sdt=5](https://scholar.google.com.hk/scholar?oi=bibs&hl=en&cites=3914196277753196289&as_sdt=5)  
* [Lee2025UNDO](https://arxiv.org/abs/2506.06278)  
  * Unlearn-Noise-Distill-on-Outputs (UNDO)  
  * Modality: language💬  
  * First unlearns, then distil  
* [Kumar2025](https://openreview.net/forum?id=fgaKGvrYUg)  
  * Modality: language💬  
* [Zhou2025Delete](https://openaccess.thecvf.com/content/CVPR2025/html/Zhou_Decoupled_Distillation_to_Erase_A_General_Unlearning_Method_for_Any_CVPR_2025_paper.html)  
  * Modality: image classification (and other classification tasks?)  
  * DEcoupLEd Distillation To Erase (DELETE)  
  * class-centric tasks  
* [Quan2025Purge](https://arxiv.org/abs/2503.22539)  
  * PURGE (Partitioned Unlearning with Retraining Guarantee for Ensembles)  
  * Verified (have guarantees?)  
  * Modality: image classification  
  * introduce constituent mapping and an incremental multi-teacher strategy that partitions the distillation process

  ## Steering Vector-based

* [Ilharco2023](https://openreview.net/forum?id=6t0Kwf8-jrj)  
  * First one to propose the idea?  
* [https://aclanthology.org/2024.acl-long.310/](https://aclanthology.org/2024.acl-long.310/)  
* [https://aclanthology.org/2024.findings-acl.107/](https://aclanthology.org/2024.findings-acl.107/)  
* [https://arxiv.org/abs/2405.03097](https://arxiv.org/abs/2405.03097)  
* [https://arxiv.org/abs/2406.17092](https://arxiv.org/abs/2406.17092)  
  * BEEAR: Embedding-based Adversarial Removal of Safety Backdoors in Instruction-tuned Language Models  
  * 

# **Evaluation, meta analysis, etc**

* [Suriyakumar2024](https://arxiv.org/abs/2410.08074)  
  * Concept revival (they term concept resurgence), Continual unlearning 🔁  
  * Specifically in Diffusion Models  
  * underscore the fragility of composing incremental model updates  
* [George2025](https://openaccess.thecvf.com/content/CVPR2025/papers/George_The_Illusion_of_Unlearning_The_Unstable_Nature_of_Machine_Unlearning_CVPR_2025_paper.pdf)  
  * Concept revival, Continual unlearning 🔁  
  * unlearned concepts will revive when the models are fine-tuned, even with general or unrelated prompts  
  * He explicitly analyses the impact of overwriting concept… calls it “mapping”  
  *   
  * Tested model: Stable Diffusion v1.4  
  * Metrics: CLIP score (between prompt and image), Classifier Accuracy (fine-tuned  
  * ViT as a binary classifier to detect the presence of the unlearned concept)  
  * Tested tasks  
    * Object Unlearning: Golf Ball, Pikachu and Dog  
    * Style Unlearning: Van Gogh, Picasso” and “Cartoon”   
    * Celebrity Unlearning: Angelina Jolie, Brad Pitt” and “Lionel Messi”.  
    * NSFW Content Unlearning: just nudity?  
  * Tested methods: SalUn, ESD, EDiff, CA, MACE, SPM, SA, Receler, UCE  
  * First intuition \- Single object finetunign  
    * Target concept “Golf Ball”  
    * Revival point: clip\>0.31  
    * We considered fine-tuning till a maximum of 91 epochs  
      ![][image26]  
  * First intuition \- Sequential object finetunining  
    * Target concept “Golf Ball”  
    * Sequence Volcano, Fish, Swimming, Hot Dog, Cricket Bat  
    * 8 epochs each  
    * Revival point: clip\>0.31  
      ![][image27]  
  * Full stuff \- Sequential object finetunining  
    * Revival point: (acc\>0.3) AND (clip \> 0.02 less than the SD’s score)  
    * For each target, identifying 10 concepts semantically related to the target (by asking GPT 4o, plus filtering by Clip)  
    * then generating the 50 images with Stable Diffusion 3 Medium for each concept  
    * general concepts appear before the more related concepts  
    * custom evaluation dataset of 20 prompts related to the unlearned concept (again generated by GPT 4o). Generated 5 images for each prompt  
    * Unearn one concept, test revival, decide if stop or go to next  
    * Uses the term “robustness” to refer to unlearning sessions taht did not revive  
      ![][image28]  
  *   
  * Conclusions  
    * MACE and UCE were relatively robust across many concepts, with less revival observed after finetuning  
    * some MU algorithms demonstrated trivial revival compared to others when fine-tuned on the same unrelated concept  
    * Which object was being finetuned was very relevant for how fast revival would happen  
    * sequential fine-tuning of concepts seems to accelerate the revival  
    * almost all methods vulnerable to fine-tuning in case of style unlearning  
    * For methods with overwrite: mapping the unlearned concept to a semantically distant or general concept enhances the model’s robustness.  
    * editing cross-attention weights alone may be insufficient for durable unlearning  
* [Huang2025](https://ieeexplore.ieee.org/document/11006878)  
  * Survey on challenges  
  * Not just for image  
  * approaches are reviewed, categorized, and discussed   
* [Lee2025UnlearningComparator](https://arxiv.org/abs/2508.12730)  
  * [https://github.com/gnueaj/Machine-Unlearning-Comparator](https://github.com/gnueaj/Machine-Unlearning-Comparator)  
  * Framwork for interactive comparison of algorithms  
  * Only image classification?  
* [Lee2025Location](https://arxiv.org/abs/2505.16252)  
  * Analyses if restricting the unelarning to a subset of parameters really helps  
  * Specially concerned about knowledge revival  
  * Focus just on language  
  * Failure of localized unlearning may stem from the absence of a uniquely responsible parameter region  
  *    
  * The usual justification for locality/sparsity is reducing inadvertent forgetting of unrelated knowledge  
  * Setup  
    * ground-truth parameter regions responsible for storing the target knowledge are explicitly predefined  
    * To decouple and eliminate localization accuracy as a confounding factor, we design a controlled experiment where the ground-truth region is explicitly predefined, allowing us to assume perfect localization  
    * Starting from the gold-standard model, finetune just one region for the desired knowledge (that will be forgotten afterwards). Tinetune anotehr region with random knowledge.  
    * Check the differences between restricting the masks to the forget-realted region vs the random-related region, respectively called Oracle and Random  
    * Each area is 10% of the parameters  
    * TOFU dataset  
    * Models: LLaMA3.1-8B-Instruct, OLMo2-7B-Instruct  
    * Unlearning methods: WGA, NPO, DPO, RMU  
    * Methods were chonse to be representative of gradient-based, preference optimization, and representation learning approaches  
  * Results  
    *  the improvement offered by Oracle over Random is marginal (with all p-values exceeding 0.3)  
    * in some cases, Random even outperforms Oracle  
      ![][image29]  
* [Li2025Edit](https://arxiv.org/abs/2505.19855)  
  * Modality: language💬  
  * conceptualize unlearning as a special case of editing where information is modified to a refusal or "empty set"  response  
  * evaluate state-of-the-art (SOTA) editing methods (e.g., ROME, MEMIT, GRACE, WISE, and AlphaEdit) against existing unlearning approaches  
* [FADE metric](https://www.semanticscholar.org/reader/2ab32ba9bfae58eda013231617f0687ddac21160)  
  * Functional Alignment for Distributional Equivalence  
  *   
  * measures the distributional alignment between unlearned and retain-only models (gold standard models)
* [Sharma2024Concealment](https://arxiv.org/abs/2409.05668) — "Unlearning or Concealment? A Critical Analysis and Evaluation Metrics for Unlearning in Diffusion Models" (Sharma, Sarkar, Chundawat, Mali, Mandal; v1 2024-09-09, v2 2024-12-12)  
  * Modality: vision🖼️ (text-to-image diffusion)  
  * Core critique: white-box analysis showing several unlearning methods only *decouple* the forgotten concept from its prompt at the text-conditioning level, without removing the concept from the model's generative capacity — the model still *can* produce it, it's just no longer reliably triggered by the original prompt. This is concealment, not forgetting; standard prompt-based evaluation (generate with the forget prompt, check if concept appears) cannot distinguish the two.  
  * **Cross-project note (added by lucas, 2026-07-02, added while auditing I-CARE knowledge):** this is the citation used in `dev-science-ops/unlearning` for our own empirical UCE finding — UCE (Gandikota2023UCE above) shows a significant *negative* Spearman correlation (r=-0.309, p=0.006) between DINOv2 embedding-specificity ratio and CLIP-based image-level forgetting on the `people` task: entities whose embedding moves *more* under UCE show *less* image-level forgetting. Read together with Sharma et al., the natural reading is that UCE's cross-attention edit shifts the internal representation (embedding moves) without reliably suppressing generation (image content survives) — i.e. it is closed-form editing that conceals more than it destroys, consistent with Sharma et al.'s critique of evaluation-metric blind spots for this class of method. Not yet written up as a formal paper claim — flagging the connection here so whoever writes the I-CARE related-work / discussion section has it, and so nobody re-derives the citation from scratch. Full numbers: see I-CARE project's own results (`assets/results/EmbeddingForgettingEfficiency/`, uce/people).

  ## Adversarial attacks

* [Liu2025Recall](https://arxiv.org/pdf/2507.07139)  
  * propose Recall, a novel adversarial framework explicitly designed to compromise the robustness of unlearned iamge generation models  
  * levrerages multi-modal conditioning  
  * optimizing adversarial image prompts with guidance from a single semantically relevant reference image  
  * modifications in the latent representation...?  
  * Tested across four representative unlearning tasks: nudity, van gogh, church, parachute  
* [Tsai2023](https://arxiv.org/abs/2310.10012)  
  * Ring-A-Bell  
  * 

  ### Prompt-level

* [Zhang2024UnlearnDiffAtk](https://arxiv.org/pdf/2409.11219)  
  * unlearned diffusion attack (UnlearnDiffAtk)  
  *   
  * designing adversarial attacks against unlearned  
  * DMs in the text prompt domain (aka jailbreaking attacks or adversarial prompts)  
  *   
  * eliminates the reliance on auxiliary diffusion or classification models  
  *   
  * leverages the concept of the diffusion classifier  
  * (utilizing the unlearned DM as a classifier); \==is this just training a naive bayes on top of the latent space of the unlearned model?==  
  *   
  *   
  * unlearning methods tested: Erased Stable Diffusion (ESD)  
  *   
  *   
  *   
  *   
  * adversarial prompts (APs) are inserted before  
  * the original prompts  
  *   
  * length of APs is restricted to only 3 ∼ 5 tokens  
  *   
  * white-box attack setting  
  *   
  * the target image itself acts as a guiding mechanism, supplying the adversarial prompt generator with the semantic information  
  * of the erased content.  
  *   
  *   
  * they currently have implemented 3 evlauation uses cases:  
  * forgetting nudify, forgetting the vangog style, forgetting 1 class of out 10 from imagenette  
  *   
  * for anything other than that, you can at most get the optimized promts (and even that is fucking difficult to separate in the code\!)  
* P4D  
  * [https://arxiv.org/abs/2309.06135](https://arxiv.org/abs/2309.06135)   
* [Zhang2025](https://arxiv.org/abs/2506.17265)  
  * Modality: multimodal💬🖼️ (language+vision)  
  * Stealthy Unlearning Attack (SUA)  
  * aims to recover the unlearned knowledge  
  * learns a universal noise pattern. When applied to input images, this noise can trigger the model to reveal unlearned content.  
  * pixel-level perturbations  
  *   
  * embedding alignment loss that minimizes the difference between the perturbed and denoised image embeddings  
  * generalizes well: a single perturbation trained on a subset of samples can reveal forgotten content in unseen images.  
* 

  ### MIA

* **Metrics**  
  * MIA (↑)  
    * Percentual  
    * Exact unlearning achives 100%  
    * munba achives 100%  
  * ASR (↓)  
    * Percentual  
    * Munba achives 3.52%  
    * For for MIA…?  
*   
*   
* [Fan2024\_challenging](https://arxiv.org/abs/2403.07362)  
  * Challenging Forgets: Unveiling the Worst-Case Forget Sets in Machine Unlearning  
  * Same author as SalUn  
  * introduce a new evaluative angle for MU from an adversarial viewpoint  
  * identifying the data subset that presents the most significant challenge for influence erasure  
  * bi-level optimization  
  * Tested datasets: CIFAR-10, 100, CelebA, Tiny ImageNet, and ImageNet  
  * Tested models: ?; both image classifiers and generative models  
  * [https://github.com/OPTML-Group/Unlearn-WorstCase](https://github.com/OPTML-Group/Unlearn-WorstCase)   
* [Zhang2024\_backdoor](https://arxiv.org/abs/2408.00929)  
  * Verification of Machine Unlearning is Fragile  
  * explore whether model providers can circumvent verification strategies while retaining the information of data supposedly unlearned  
  * categorize the current verification strategies regarding potential dishonesty among model providers:  backdoor verification and reproducing verification  
  *  introduce two novel adversarial unlearning processes capable of circumventing both types  
  * validate the efficacy of our methods through theoretical analysis and empirical experiments  
* [Zhang2024\_AdvUnlearn](https://arxiv.org/abs/2405.15234v1)  
  * Same research group as Salun  
  * *Defensive Unlearning with Adversarial Training for Robust Concept Erasure in Diffusion Models*  
  * [https://github.com/OPTML-Group/AdvUnlearn](https://github.com/OPTML-Group/AdvUnlearn)   
  * adversarial prompt attacks: prompts that can make an “unlearned” model to still generate undesired images containing concepts meant to be erased  
  * framework referred to as AdvUnlearn  
  * develop a utility-retaining regularization on an additional retain set, optimizing the trade-off between concept erasure robustness and model utility  
  * Experiments: erasure of nudity, objects, and style concepts  
  * Tested models: Stable Difusion?  
  *   
* [Zhang2024\_UnlearnDiffAtk](https://arxiv.org/abs/2310.11868)  
  * Same first author as AdvUnlearn  
  * Same research group as Salun  
  * *To Generate or Not? Safety-Driven Unlearned Diffusion Models Are Still Easy To Generate Unsafe Images ... For Now*  
  * [https://github.com/OPTML-Group/Diffusion-MU-Attack](https://github.com/OPTML-Group/Diffusion-MU-Attack)   
  * introduce an evaluation framework  
  * leverages adversarial prompts to discern the trustworthiness of unlearned models  
  * adversarial prompt generation approach for DMs  
* [Wang2025IAM](https://arxiv.org/abs/2506.06112)  
  * Modality: ?  
  * Not exactly MIA attack, I think, but similar logic  
  * quantifies sample-level unlearning completeness by interpolating the model's generalization-fitting behavior gap on queried samples  
    

  ## 

  ## Benchmarks

* **SemEval-2025 Task 4**  
  * titled "Unlearning sensitive content from Large Language Models."  
  * Language  
  * Yearly competition?  
* [Zhang2024UnlearnCanvas](https://arxiv.org/abs/2402.11846)  
  * Dataset for Image Unlearning Evaluation  
  * high-resolution stylized image dataset that facilitates the evaluation of the unlearning of artistic styles and associated objects.  
  * 7 quantitative metrics  
  * Includes adversarial prompts, the unlearning of finer-scale concepts, and sequential unlearning  
  * Tested across benchmark 9 state-of-the-art MU methods for DMs  
  * [Webpage](https://unlearn-canvas.netlify.app/)  
  * [https://github.com/OPTML-Group/UnlearnCanvas](https://github.com/OPTML-Group/UnlearnCanvas)   
  * Tasks: 60 artistic painting styles, 20 objects (including in each of the styles?)  
  * Tested algorithms: ESD, CA, UCE, FMN, SalUn, and SA  
  *    
  *  inputs the fine-tuned SD with the prompt: “A \[object name\] in \[style name\] style,” to generate 20 images for each object-style pair, resulting in 24,000 images in total (as there are 1,200 object-style pairs)  
* [Liu2025EvalIGMU](https://arxiv.org/pdf/2506.02761)  
  * standard tasks and metrics for evaluation, including dataset  
  * EvalIGMU and DataIGM  
  * [https://github.com/ryliu68/IGMU](https://github.com/ryliu68/IGMU)   
  * Tasks: Nudity, Style (129 artists… but the code only works for VG?), Object (10 from imagenette… but the code only works for parachute and church?)  
  * Tested algorithms: ESD, FMN, SPM, AdvUnlearn, MACE, RECE, DoCo, Receler, ConceptPrune, UCE  
  * Categorization of tasks:  
    ![][image30]  
    ![][image31]  
    ![][image32]  
* [Jeung2025Dusk](https://arxiv.org/abs/2505.15209)  
  * Modality: language💬  
  * evaluate unlearning methods under realistic data overlap  
  * Do not assume that forget and retain sets are fully disjoint  
  * while most can remove surface-level text, they often fail to erase deeper, context-specific knowledge without damaging shared content  
  * Do not discuss entanglement, only data co-occurrence  
* [Kawakami2025](https://arxiv.org/abs/2507.01271)  
  * Modality: multimodal💬🖼️ (language+vision)  
  * PULSE  
  * Focus on (i) Pre-trained knowledge Unlearning for analyzing the effect across different knowledge acquisition phases and (ii) Long-term Sustainability Evaluation to address sequential requests  
* [Chen2025ActPert](https://arxiv.org/abs/2505.23270)  
  * Modality: language💬  
  * Activation Perturbation-based Auditing (ActPert)  
  * Specifically concerned about knowledge revival?  
  * propose a novel activation perturbationbased auditing method  
* [Moon2024HUB](https://www.semanticscholar.org/paper/Holistic-Unlearning-Benchmark%3A-A-Multi-Faceted-for-Moon-Lee/8ebb6f03968a79190217b6500b0068d50ffa076b)  
  * Holistic Unlearning Benchmark (HUB)  
  * for evaluating unlearning methods across six key dimensions: faithfulness, alignment, pinpoint-ness, multilingual robustness, attack robustness, and efficiency  
  * Modality: text-to-image  
* [Chen2025nsfw](https://export.arxiv.org/pdf/2505.15450v2)  
  * Specific for NSFW  
  * full-pipeline toolkit specifically designed for NSFW concept erasure  
  * Modality: text-to-image  
* **FaithUn**  
  * See in [Yang2025](https://arxiv.org/abs/2502.19207)  
* **ForgetMe**  
  * [https://arxiv.org/pdf/2504.12574](https://arxiv.org/pdf/2504.12574)  
  * [https://github.com/YuZhenyuLindy/ForgetMe](https://github.com/YuZhenyuLindy/ForgetMe)  
  * 

  ## Applications

  [https://arxiv.org/html/2410.08069v1](https://arxiv.org/html/2410.08069v1): Unlearning-based Neural Interpretations

# **Non unlearning related literature**

*   
* [Martens2015](https://arxiv.org/abs/1503.05671)  
  * Kronecker-factorized approximation, or Kronecker-factored Approximate Curvature (K-FAC)  
  * FIM is too large and expensive to calculate (because it scales quadratically with the number of paramers, e.g. a network with 100k parameters would require storing and estimating 1B elements in the matrix)  
  * insofar as the loss space is locally \+- quadratic, Conjugate Gradients can be faster than SGD  
  *   
*   
*   
* [singh2020woodfisher](https://arxiv.org/abs/2004.14340)  
  * Woodfisher method  
  * to approximate the inverse of the hessian  
* [https://huggingface.co/blog/dreambooth](https://huggingface.co/blog/dreambooth)   
  * tutorial  
  * Dreambooth training using Diffusers  
  * not very systematic, but very illustrative  
* Oikarinen2023  
  * Location knowledge in CLIP  
* Goh2021  
  * Location knowledge in CLIP  
  * 


  


  

* [https://transformer-circuits.pub/2025/linebreaks/index.html](https://transformer-circuits.pub/2025/linebreaks/index.html)  
  * investigate the mechanisms that enable Claude 3.5 Haiku to perform a natural perceptual task  
  * The task we study is linebreaking in fixed-width text  
  * To orient ourselves to the stages of the computation, we first studied the model using discrete dictionary feature  
  * Our work demonstrates the intricate ways in which these manifolds can be manipulated to perform *computation*  
  *    
  * created a synthetic dataset using a text corpus of diverse prose where we (1) stripped out all newlines and (2) reinserted newlines every k characters  
  * We define the *line character count* (or *character count*) at a given token in a prompt to be the total number of characters since the last newline  
  * They were able to predict character count with high accuracy via linear regression on the residual stream


  **Fisher Information Matrix (FIM):**

* measures the amount of information contained in a dataset about the parameters of a probability distribution  
* used to estimate how sensitive a model's parameters are to changes in the data  
* matrix of second cross-moments of the score vector, which is the vector of first partial derivatives of the log-likelihood function with respect to its parameters  
* same dimension as the parameters  
* Parameters with high Fisher Information are more sensitive to changes in that data  
* Properties  
  * Positive Semidefinite  
  * Under mild regularity conditions, the FIM is equal to the covariance matrix of the score vector.  
  * Information Orthogonality: Two parameter component vectors are information orthogonal if the FIM is block diagonal, with these components in separate blocks  
  * Regular vs. Singular Models: A statistical model is regular if the FIM is positive definite for all parameters, and singular otherwise. Regular models are easier to analyze and estimate.

  ## Continual learning

* [Kirkpatrick2016](https://arxiv.org/abs/1612.00796)  
  * [https://www.pnas.org/doi/10.1073/pnas.1611835114](https://www.pnas.org/doi/10.1073/pnas.1611835114)  
  * Proposes EWC  
  * In the context of sequential learning  
  * remembers old tasks by selectively slowing down learning on the weights important for those tasks  
  * regularization that result in penalizing large changes in parameters or activatio  
  *   
* [Liu2018](https://arxiv.org/abs/1802.02950)  
  * Rotated EWC  
  * In the context of sequential learning, but have some neat ideas we can use  
  * [blog post](http://www.lherranz.org/2018/08/21/rotating-networks-to-prevent-catastrophic-forgetting/)  
* [li2016lwf](https://arxiv.org/pdf/1606.09282)  
* [wang2024mineganpp](https://link.springer.com/article/10.1007/s11263-023-01882-y)

  ## Transfer learning

* [Zhang2020survey](https://arxiv.org/abs/2009.00909)  
  * [https://www.ieee-jas.net/article/doi/10.1109/JAS.2022.106004](https://www.ieee-jas.net/article/doi/10.1109/JAS.2022.106004)   
  * Negative transfer  
* [ouyang2024TGDP](https://proceedings.neurips.cc/paper_files/paper/2024/file/f782860c2a5d8f675b0066522b8c2cf2-Paper-Conference.pdf)  
  * Modality: image generation 🖼️  
  * introduces the Transfer Guided Diffusion Process (TGDP), a novel approach distinct from conventional finetuning and regularization method

  ## Parameter efficient finetuning

* [Hu2021](https://arxiv.org/abs/2106.09685): Original LoRa paper  
* [Xu2023](https://arxiv.org/abs/2312.12148): Review  
* [Muñhoz2024](https://arxiv.org/abs/2410.03750)  
  * SQFT (Sparse Quantized Fine Tuning?)  
  * Also proposes Sparse Parameter-Efficient Fine-Tuning (SparsePEFT)  
  * end-to-end solution for low-precision sparse parameter-efficient fine-tuning   
  * enables the merging of sparse weights with low-rank adapters without losing sparsity nor accuracy  
  *  also addresses the challenge of having quantized weights and adapters with different numerical precisions  
  * [https://github.com/IntelLabs/Hardware-Aware-Automated-Machine-Learning/tree/main/SQFT](https://github.com/IntelLabs/Hardware-Aware-Automated-Machine-Learning/tree/main/SQFT)  
  * “when LoRA is combined with model compression techniques, e.g., sparsity or quantization, several challenges prevent merging these adapters into a single compressed and fine-tuned model”  
  * LPMs \= Large pre-trained models  
    ![][image33]  
    ![][image34]  
  * Uses a Neural Low-rank Adapter Search (NLS) instead of vanilla LoRA (no need to hardcode rank or target weights); past publication; different parameters per target  
    ![][image35]  
  *   
  * SparsePEFT  
    * a component of SQFT; address the adapter merging  
    * make adapters sparsity-aware  
    *  applies a binary mask M derived from the initial sparsification of W. This mask is used to sparsify the adapters matrix BA into Lp: ![][image36]  
    * A binary mask is obtained from the sparsified weights and applied to the adapters, allowing for the later merge without loss of sparsity  
    * Train Lp normally form then on  
    * The mask is active during the fine-tuning process  
  * Quantization-aware SparsePEFT  
    *  integrates quantization awareness  
  * Evaluation  
    * Models:  Llama-3-8B, Mistral-7Bv0.3 and Phi-3-Mini-4K-Instruct  
    * Datasets: math (GSM8K, MAWPS, SVAMP), reasoning (BoolQ, PIQA, HellaSwag, WinoGrande, Arc-e, OBQA)  
    * compare with vanilla LoRA and GPTQ \+ LoRA  
      ![][image37]

* [wu2025sdlora](https://arxiv.org/html/2501.13198v3)  
  * LoRA for continual learning (specifically for class incremental learning, without rehearsal)  
  * Scalable Decoupled LoRA  
  * (+) excellent stability-plasticity trade-off  
  * (+) mitigates catastrophic forgetting  
  * [https://github.com/WuYichen-97/SD-Lora-CL](https://github.com/WuYichen-97/SD-Lora-CL)  
  *   
  * during learning on task t, SD-LoRA computes the output \`h=(W0 \+ AB)x\` by  
    ![][image38]  
  *   
  *   
  * can also be viewed as a form of model-merging techniques  
  * incrementally decouples the learning of the magnitude and direction of LoRA components, while fixing the directions learned from previous tasks as CL progresses  
  * selectively scales the parameter update along the previously learned directions, effectively enabling the classifier to trace a low-loss path that ultimately settles on an overlapping low-loss region for all tasks  
  *    
* [Staniszewski2025](https://www.semanticscholar.org/reader/8aeb268497023392ec6688c43666f7ee00f9cef0)  
  * LoRA for continual learning  
  * tackle the problem of continual customization under a rigorous regime with no access to past tasks’ adapter  
  * investigate how different adapters’ initialization and merging methods can improve the quality of the final model  
  * [https://github.com/luk-st/continual-lora](https://github.com/luk-st/continual-lora)   
    ![][image39]  
  * Approach 1  
    * Naïve continual finetuning of the low-rank adapter  
    * without any reinitialization  
  * Approach 2  
    * consecutive merging of task-specific adapters  
    * create a new LoRA adapter for each task  
    * Random initialization  
    * reduces task interference  
  * Approach 3  
    * merging LoRAs initialized with orthogonal weights  
    * high plasticity but low stability  
  * Approach 4  
    * merging through a selection of weights with the highest magnitude for the task  
    * low plasticity but high stability  
  *   
  *    
  * Eval 1: objects  
    * cosine similarity between model outputs and reference images with DINO and CSD  
  * Eval 2: style  
    * Dataset: Unlearn Canva  
    * perform fine-tuning on the 10 consecutive tasks and average results over 4 random tasks ordering, with 2 random seeds each  
    * Metrics: cosine similarity between model outputs and reference images with DINO and CLIP  
    *  report the performance of the final model fine-tuned over all 10 tasks with the Average Score and Average Forgetting metrics


  ## Bias

* [https://pmc.ncbi.nlm.nih.gov/articles/PMC12032156/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12032156/)   
  * evaluated 10k generated faces under the prompt “a photo of a person”, finding 65% male vs 35% female  
  * Proposes debiasing solution  
  * Also analyses if individuals of the same race are depicted as being too similar to one another  
  *   
* [https://arxiv.org/abs/2211.03759](https://arxiv.org/abs/2211.03759)  
  * broad range of ordinary prompts produce stereotypes  
* [https://aclanthology.org/2023.findings-acl.160/](https://aclanthology.org/2023.findings-acl.160/)  
  * we seek to measure more complex human biases exist in the task of text-to-image generations.  
  * Inspired by the well-known Implicit Association Test (IAT) from social psychology, we propose a novel Text-to-Image Association Test (T2IAT) framework that quantifies the implicit stereotypes between concepts and valence  
* [https://aclanthology.org/2023.findings-emnlp.465/](https://aclanthology.org/2023.findings-emnlp.465/)  
  * Using CLIP-cosine similarity for zero-shot classification of images generated by CLIP-based Stable Diffusion v2.1  
* [Birhane2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/42f225509e8263e2043c9d834ccd9a2b-Paper-Datasets_and_Benchmarks.pdf)  
  * Dataset Audit  
  * investigate hateful content differences between LAION-400M and LAION-2B  
  * focused on the alt-text  
  * [https://github.com/vinayprabhu/hate\_scaling](https://github.com/vinayprabhu/hate_scaling)  
  * Experiment design  
    * Sub-sample 100k image rows from both datasets and extract the alt-text descriptions  
    * 3.2 million samples for the LAION-400M, 12.8 million samples for the LAION-2B-en dataset  
    * Infer toxicity scores (hateful, targeted, aggressive) with lib pysentimiento  
    * check if any of the relevant scores exceeds a predefined threshold  
    * Hate Content Rate (HCR): percentage of samples that failed the check  
  * Results  
    * hate content increased by nearly 12%  
    * basic filtering (using the NSFW existing classification) still left a consirable amount of aggressive content  
    * Wilson Score to calculate estimation bounds  
      ![][image40]  
      ![][image41]

    
* [Turk2023](https://restofworld.org/2023/ai-image-stereotypes/)  
  * Blog post  
  * How AI reduces the world to stereotypes  
* [https://dl.acm.org/doi/10.1145/3613904.3642877](https://dl.acm.org/doi/10.1145/3613904.3642877)  
  * the culture of a disadvantaged country is prone to be neglected, some specified subjects often present a stereotype or a simple patchwork of elements, and over half of cultural objects are mispresented.  
* [https://arxiv.org/pdf/1907.09754](https://arxiv.org/pdf/1907.09754)  
  * Luis’  
  * Controlling biases and diversity in diverse image-to-image translation  
* [BiasMap](https://spexlab.org/files/BiasMap_cvpr2025.pdf)  
  * for uncovering latent concept-level representational biases in stable diffusion  
  * leverages cross-attention attribution maps to reveal structural entanglements between demographics (e.g., gender, race) and semantics (e.g., professions) concepts  
  * bias discovery method  
  * Prompt used: “A photo of the face of a \[profession\] and \[race/gender\]”  
  * Based on OVAM  
  * Intuition: If concept entanglement exists between demographics and semantics, the attention maps should have substantial intersection over spatial regions.  
  * Tested 3 models: SD v1.5, FD, IG  
  * Metrics: mIoU ↓, mBIoU ↓, RD  ↓  
* [Shi2025](https://arxiv.org/html/2503.20483v1)  
  * Propose DiffLens  
  * bias mitigation  
  * analyzes the architectural components to identify the most influential elements within the model  
  * we hypothesize that neurons collectively play a pivotal role in driving the generation of biased concepts.  
  * [Shi2025.pdf](https://drive.google.com/file/d/1V4ly6b9xI1Sz7Yr0s_POpeUkwegOchzf/view?usp=drive_link)  
  *    
  * Tested models: P2 (unconditional), Stable Diffusion  
  * Metrics: Fairness Discrepancy (FD), FID (iamge quality), Clip-T (similarity between the generated image and the input text prompt), CLIP-I (similarity between originally generated images and images after debiasing)  
  * Biases: Gender, Age, Race  
  *   
  *   
  *   
  * disentangles the hidden neurons of the diffusion model into a sparse semantic feature space via a sparse autoencoder  
  * Gradient-based approach to pinpoint key components in the interpretable semantic space  
  * mitigate the bias by adjusting the effects of these bias-related features  
    ![][image42]  
* [Zhuang2024](https://arxiv.org/abs/2409.19967)  
  * propose Magnet, a novel training-free approach to tackle the attribute binding problem  
  * Use positive and negative binding vectors to enhance disentanglement, further with a neighbor strategy to increase accuracy  
  * [Zhuang2024.pdf](https://drive.google.com/file/d/1ilCCU1XKb-zurj29a-eagskh3miBVZTa/view?usp=drive_link)  
  * How the text encoder understands attribute, and how it affects the attribute binding of T2I diffusion models.  
  * Our manipulation is performed strictly in the textual space, without training, fine-tuning, or additional datasets and inputs  
    ![][image43]  
* [Jaaskelainen2025](https://link.springer.com/article/10.1007/s00146-025-02207-y)  
  * analyze Stable Diffusion (SD)  
  * Our analysis covers; (1) the aesthetics of the AI-generated visual material, (2) the institutional contexts in which these images are situated and produced, and (3) the intersections between power systems such as racism, colonialism, and capitalism  
  * Generrated 180 images  
  * interpretative qualitative analysis  
  * [Jaaskelainen2025.pdf](https://drive.google.com/file/d/1IEzsrZvHosknlOrZcbUXpdwWye9fz-FD/view?usp=drive_link)  
    ![][image44]  
* [Luccioni2023](https://arxiv.org/abs/2303.11408)  
  * Proposes Stable Bias  
  * method for exploring the social biases in text-to-image systems  
  * characterizing the variation in generated images triggered by enumerating gender and ethnicity markers in the prompts  
  * [Luccioni2023.pdf](https://drive.google.com/file/d/1xElamhHulsyY_cQESo7S4D5EfVCXHuLN/view?usp=drive_link)  
  *   
  * Models: Dall·E 2, Stable Diffusion v 1.4 and 2  
  * Attributes: gender and ethnicity.  
  * generate images by using prompts along those attributes  
  * 146 occupations drawn from the U.S. Bureau of Labor Statistics, using prompts like “Photo portrait of a \[occupation\]”  
  * HuggingFace “stable-bias/professions-v2”  
  * Evaluation  
    *  a text-based analysis that leverages Visual Question Answering (VQA) models in the text modality  
    * answers the question “What word best describes this person’s appearance?”  
    *   
    * clustering-based evaluation to characterize correlations between social attributes and identity characteristics directly in the image modality  
    * Use BLIP to obtain image embeddings  
    *   
  *   
  * Results  
    * consistently under-represent marginalized identities  
* [Sun2025Bias](https://arxiv.org/abs/2506.00253)  
  * Bias mitigation  
  * In contrast to conventional mitigation methods of machine unlearning, our interventions find that steering the model to be more aware of racial concepts effectively mitigates implicit bias  
  * Similar to race blindness in humans, ignoring racial nuances can inadvertently perpetuate subtle biases in LMs.  
* [Inca2024OpenBias](https://openaccess.thecvf.com/content/CVPR2024/papers/DInca_OpenBias_Open-set_Bias_Detection_in_Text-to-Image_Generative_Models_CVPR_2024_paper.pdf)  
  * pipeline that identifies and quantifies the severity of biases agnostically, without access to any precompiled set.  
  * https://github.com/Picsart-AI-Research/OpenBias  
  * Example of the type of bias they can find: tendency of the generator to produce content of a certain class c (e.g. “man”), given a textual prompt t that does not specify the intended class (e.g. “A picture of a doctor”).  
  * open-set scenario: without constraints (or data collection) for a specific predefined set of biases  
  *   
  *   
  * In the first phase, we leverage a LLM to propose biases given a set of captions.   
  * Secondly, the target generative model produces images using the same set of captions.   
  * Lastly, a Vision Question Answering model recognizes the presence and extent of the previously proposed biases.  
  *    
  * Tested models: Stable Diffusion 1.5, 2, and XL  
* **demographic parity**  
  * Fairness… definition? Metric?  
  * a model should ensure the same ratio of positive outcomes across sensitive groups  
  * (-) overlooking the real data distributions  
* **Equal opportunity**  
  * Fairness… definition? Metric?  
  * ensuring the equality of True Positive Rates (TPR) across sensitive groups  
  * (-) does not address the imbalance of negative outcomes  
* **equalized odds (EO)**  
  * Fairness metric  
  * equally consider positive and negative outcomes  
    ![][image45]

    
    
* **Fairness Discrepancy (FD)**  
  * metric  
  * Rishubh Parihar, Abhijnya Bhat, Abhipsa Basu, Saswat  
  * Mallick, Jogendra Nath Kundu, and R Venkatesh Babu. Bal-  
  * ancing act: Distribution-guided debiasing in diffusion mod-  
  * els. In Proceedings of the IEEE/CVF Conference on Com-  
  * puter Vision and Pattern Recognition, pages 6668–6678,  
  * 2024\. 1, 2, 4, 5, 6, 7, 9, 11  
  *   
  * calculates the Euclidean distance between a reference distribution (typically uniform) and the bias distribution of generation, representing class distributions within an attribute (e.g., male and female for gender attribute)  
* **Visual Prompt Tuning (VPT)**  
  * approach for adapting the pre-trained transformer models to downstream computer vision tasks  
  * efficient  
  * incorporates learnable parameters in the input space of ViT  
  * freezing the ViT backbone and tuning only the prompts  
* [Park2024fairvpt](https://openaccess.thecvf.com/content/CVPR2024/papers/Park_Fair-VPT_Fair_Visual_Prompt_Tuning_for_Image_Classification_CVPR_2024_paper.pdf)  
  *  removes biased information in the pre-trained ViT while adapting it to downstream classification tasks  
  *    
  * categorize prompts into “cleaner prompts” (encoded to contain biased information from the pre-trained model) and “target prompts” (not correlated with the sensitive attribute)  
  * encode the class token in two different ways by either masking or not masking the target prompts in the self-attention process  
  * encoded tokens are trained with distinct objective functions  
  * Disentanglement loss. Decorrelate the losses of the two tasks?  
    ![][image46]  
  * Model: ViT-B/16 backbone pre-trained on ImageNet-21k; Then finetuned to classify the Target Attributes… AND sensitive attribute?  
  * Dataset: CelebA  
  * Metrics: classification accuracy for the target attribute, Equalized Odds (for fairness)  
  * Chosen sensitive attributes (SA): gender, …what else?  
  * Chosen target attributes (TA?): Attractive, Big Nose (chosen by min correlation with SA?)  
  * Compared methods: VPT, VPT-Head+NCM, ViT+NCM  
  *    
  * Other tested datasets (??):  UTK Face \[60\], bFFHQ \[30\], and Waterbirds  
* [https://openaccess.thecvf.com/content/CVPR2025/papers/Li\_T2ISafety\_Benchmark\_for\_Assessing\_Fairness\_Toxicity\_and\_Privacy\_in\_Image\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Li_T2ISafety_Benchmark_for_Assessing_Fairness_Toxicity_and_Privacy_in_Image_CVPR_2025_paper.pdf#:~:text=prompt%20is%20shown%20in%20Section,using%20T2I%20models%20listed%20in)  
  * T2ISafety: Benchmark for Assessing Fairness, Toxicity, and Privacy in Image Generation  
  * The T2ISafety benchmark uses the FACET and FairFace image sets (32K and 22K images with gender/race/age labels) as “real” references,  
* **Diffusion Bias Explorer**  
  * [https://huggingface.co/spaces/society-ethics/DiffusionBiasExplorer](https://huggingface.co/spaces/society-ethics/DiffusionBiasExplorer)   
* **IAT**  
  * measures the differential relationships between a target concept and an attribute  
  * Image Embedding Association Test (iEAT)  
    * Extended to the image domain  
    * [https://pubmed.ncbi.nlm.nih.gov/28408601/](https://pubmed.ncbi.nlm.nih.gov/28408601/)  
    * [https://openaccess.thecvf.com/content\_ECCV\_2018/papers/Mathilde\_Caron\_Deep\_Clustering\_for\_ECCV\_2018\_paper.pdf](https://openaccess.thecvf.com/content_ECCV_2018/papers/Mathilde_Caron_Deep_Clustering_for_ECCV_2018_paper.pdf)   
    * measures the differential association of the target concepts X and Y with the attributes A and B based on the image embeddings obtained by feeding images representing these concepts and attributes to a trained deep learning model.   
    * For instance, let the chosen target concepts be insect (X) and flower (Y) and the attributes be unpleasant (A) and pleasant (B). Then, the association test will measure the strength of correlation between insect and unpleasant, and flower and pleasant based on the cosine distances between the embeddings of X, Y, A and B


  


  US Bureau of Labor Statistics (BLS) percentages of men and women in these professions: [https://www.bls.gov/cps/cpsaat11.htm](https://www.bls.gov/cps/cpsaat11.htm) 

  Used in several papers, like [https://proceedings.neurips.cc/paper\_files/paper/2023/file/b01153e7112b347d8ed54f317840d8af-Paper-Datasets\_and\_Benchmarks.pdf\#:\~:text=the%20identity%20characteristics%20%E2%80%94%20ethnicity,a%20list%20of%20146%20occupations](https://proceedings.neurips.cc/paper_files/paper/2023/file/b01153e7112b347d8ed54f317840d8af-Paper-Datasets_and_Benchmarks.pdf#:~:text=the%20identity%20characteristics%20%E2%80%94%20ethnicity,a%20list%20of%20146%20occupations)

  And [https://arxiv.org/abs/2303.11408](https://arxiv.org/abs/2303.11408) 

  *   
  * 


  ## Entanglement

* [https://proceedings.mlr.press/v202/zhang23ak.html](https://proceedings.mlr.press/v202/zhang23ak.html)  
  * Theoretical view, naming  
  * using category theory as a unifying framework  
* [https://arxiv.org/abs/2210.04885](https://arxiv.org/abs/2210.04885)  
  * Proposes interpretability method DAAM  
  * pixel-level attribution maps  
  * Analyze Stable Diffusion  
  * Evaluated by their segmentation quality?  
  * Also studies feature entanglement  
    * find that cohyponyms worsen generation quality  
    * Example: “a giraffe and a zebra” generates either a giraffe or a zebra, but not both.  
    * used WordNet (Miller, 1995\) to construct a hierarchical ontology expressing semantic fields over COCO’s 80 visual objects  
    *   
    * Also, If we hold the scene layout fixed and vary only the adjective, the entire image changes, not just the noun  
* [https://wuqiuche.github.io/DiffusionDisentanglement-project-page/](https://wuqiuche.github.io/DiffusionDisentanglement-project-page/)  
  * propose an image editing algorithm where the mixing weights of the two text embeddings are optimized for style matching and content preservation  
  * Is it basically adding a task vector…?  
  * Allow small semantic edits, akind to changing the latent space of GANs  
* [Yu2025](https://arxiv.org/html/2508.08879v1)  
  * LLM (llama)  
  * propose Culturescope, the first mechanistic interpretability-based method that probes the internal representations of LLMs to elicit the underlying cultural knowledge space  
  * probe internal representations and surface the cultural knowledge activated during cultural understanding tasks  
  * Study how LLMs internalize Western-dominance bias and cultural flattening  
  * introduce a cultural flattening (CF) score  
  * [Yu2025.pdf](https://drive.google.com/file/d/1LGb2HRBhRjqxjbBSEc8BYLAdboL7iIzA/view?usp=drive_link)  
  *   
  * LLM answer to an Open-Ended cultural QA  
  * compute the representative hidden representations used to generate an answer  
    ![][image47]  
* [Chandna2025](https://arxiv.org/html/2506.05166v2)  
  * mechanistic interpretability approach to analyze how such biases are structurally represented within models  
  * Models: GPT-2 Small, GPT-2 Large, and Llama2  
  * LLM  
  * Uses Edge Attribution Patching  
  * DSS1, DSS2, etc: prompts / tested biases  
  * [Chandna2025.pdf](https://drive.google.com/file/d/12wb7ql_4aPo5rmYXDF6Mx_HsE6GT7r4c/view?usp=drive_link)  
  * Demographic setup  
    * Prompts: Afghan people are so \_\_\_, As expected, Afghan people are so \_\_\_  
    * Check sentiment with Distilbert-base-uncased  
  * Gender setup  
    * Prompts: The doctor did a mistake, and everyone scolded \_\_\_, The doctor did a miracle, and everyone praised \_\_\_  
    * 320 professions  
    * check the predicted token with a set of male and female words  
  * Results  
    * Bias-related computations are highly localized, often concentrated in a small subset of layers  
    * only a few layers contribute to the important edges for bias  
    *  there is minimal to no overlap between demographic and gender biases.  
    *   
      ![][image48]  
      ![][image49]  
  *   
*   
* [https://openreview.net/pdf?id=hv82NTjEhs](https://openreview.net/pdf?id=hv82NTjEhs)  
  * Bias Spillover in Language Models  
  * Review  
  * Focus on Political Alignment, Regional Fragility, and Multi-Axis Risks  
  * bias spillover: unintended alteration of behavior on one social axis when mitigating another; interventions along one axis propagating to others  
  * [5210\_Bias\_Spillover\_in\_Languag.pdf](https://drive.google.com/file/d/1t_iTtFPJxiz9zHOFRk7GAaTs9qOlb3BM/view?usp=drive_link)  
  * Mechanisms that contribute to spillover  
    * Entangled embeddings during pretraining: shared subspaces  
    * Conflicting fine-tuning objectives and shared adaptation pathways: opposing gradients  
    * Shared parameter update: ?  
    * Intersectional bias and multi-axis interactions: models may appear unbiased on single attributes but show strong bias at intersections (e.g., Black women)  
  * Potential auditing methods for detecting identity entanglement and bias spillover in LLMs:  
    ![][image50]  
  * Conceptual schematic:  
    ![][image51]  
* 

  ## Generic datasets

* Suumary os attribute datasets: [https://sites.ecse.rpi.edu/\~cvrl/database/AttributeDataset.htm\#:\~:text=Attributes%3A%2064%20types%20of%20binary,and%20the%20aYahoo%20test%20set](https://sites.ecse.rpi.edu/~cvrl/database/AttributeDataset.htm#:~:text=Attributes%3A%2064%20types%20of%20binary,and%20the%20aYahoo%20test%20set)   
* [SUNAttributes](https://sci-hub.box/https://ieeexplore.ieee.org/document/6247998%20)  
  * Scenes  
  * Scene UNderstanding (SUN)  
  * subset of the SUN Database for fine-grained scene categorization  
  * 14,340 images from 717 classes (20 images per class).  
  * Each image is annotated with 102 binary attributes that describe the scenes’ material and surface properties (lighting conditions, functions, affordances, and general image layout)  
  * Well stablished  
  *   
  * every scene has independent attribute labels  
  * global, binary attributes  
  * taxonomy of more than 100 scene attributes from crowd-sourced experiments (asking to write features taht could distinguish two distinct classes, then filter and joining synonyms)  
  * They consider it valid to “averaging the binary labels from multiple annotators we produce a real-valued confidence for each attribute”  
  * Most attributes fall into (1) Materials (e.g. cement, vegetation), (2) surface properties (e.g. rusty) (3) functions or affordances (e.g. playing, cooking), (4) spatial envelope attributes (e.g. enclosed, symmetric), and (5) object presence (e.g. cars, chairs).  
  * Annotated on Amazon Mechanical Turk  
  *    
  * Each image has a attribute occurance vectors;real-valued labels ranging from 0-1, which correspond to how often a given attribute was voted as being present in a given image by Mechanical Turk Workers. These continuous values are  calculated from 3 votes given by the AMT workers for each image.  
  * First SUN paper: [https://sci-hub.box/https://ieeexplore.ieee.org/document/5539970](https://sci-hub.box/https://ieeexplore.ieee.org/document/5539970)   
  *    
  * Annotations design  
    * workers are presented with a grid of 4 dozen images and are asked to consider only a single attribute at a time  
    * click on images which exhibit the attribute in question  
    * use several techniques to filter out bad workers and then cultivate a pool of trusted workers  
    * Any worker whose average number of labels or work time for a given attribute is greater than one standard deviation away from the average for all workers is added to a list of workers to manually review  
    * identify a smaller group of 38 trusted workers out of the ∼800 who participated. They got more money  
  * PCA of features:  
    ![][image52]  
      
* [PACO](https://github.com/facebookresearch/paco/blob/main/docs/PACO_DATASET.md)  
  * Objects  
  * **Interesting attributes**: \['black', 'light\_blue', 'blue', 'dark\_blue', 'light\_brown', 'brown', 'dark\_brown', 'light\_green', 'green', 'dark\_green', 'light\_grey', 'grey', 'dark\_grey', 'light\_orange', 'orange', 'dark\_orange', 'light\_pink', 'pink', 'dark\_pink', 'light\_purple', 'purple', 'dark\_purple', 'light\_red', 'red', 'dark\_red', 'white', 'light\_yellow', 'yellow', 'dark\_yellow', 'other(color)', 'plain', 'striped', 'dotted', 'checkered', 'woven', 'studded', 'perforated', 'floral', 'other(pattern\_marking)', 'logo', 'text', 'stone', 'wood', 'rattan', 'fabric', 'crochet', 'wool', 'leather', 'velvet', 'metal', 'paper', 'plastic', 'glass', 'ceramic', 'other(material)', 'opaque', 'translucent', 'transparent', 'other(transparency)'\]  
* [Qi2024](https://arxiv.org/pdf/2409.06300)  
  * Objects  
  * **Interesting attributes**  
    * Color: black, blue, brown, gray, green, orange, pink, red, tan, violet, white, yellow  
    * Material: asphalt, ceramic, glass, leather, metal, paper, polymers, stone, textile, wood  
    * Tone / Texture: light, dark, soft, smooth  
    * State: wet, open, piece, on, off, full, folded, empty, dry, dilapidated, cracked, covered, closed  
* [ImageNet](https://www.image-net.org/download-attributes.php)  
  * Objects  
  * **Interesting attributes**  
    * Color: black, blue, brown, gray, green, orange, pink, red, violet, white, yellow  
    * Pattern: spotted, striped  
    * Shape: long, round, rectangular, square  
    * Texture: furry, smooth, rough, shiny, metallic, vegetation, wooden, wet  
    * No class-specific attributes  
    *   
    * Plus the wordnet hierarchy  
  * **Important subsets**  
    * ILSVRC65; simplified hierarchy  
    * ILSVRC1K  
    * ImageNet10K  
      ![][image53]  
* [ScanNet](http://www.scan-net.org/)  
  * Objects  
  * **Interesting attributes:** size, …what else?  
* Large-scale Attribute Dataset (LAD)  
  * 50 categories of vehicles, 50 electronics, 50 fruits, 50 animals, 30 hair styles  
  * [https://arxiv.org/abs/1804.04314](https://arxiv.org/abs/1804.04314)   
  * https://drive.google.com/drive/folders/1WU2dld1rt5ajWaZqY3YLwLp-6USeQiVG  
* Objects365-Attr  
  * Objects  
  * 365 categories  
  * 5.6M object-level attribute descriptions, meticulously annotated across 1.4M bounding boxes.  
* **DeepFashion**  
  * 50 classes  
  * [https://complexity.cecs.ucf.edu/deepfashion](https://complexity.cecs.ucf.edu/deepfashion)  
* **aPascal & aYahoo**  
  * 32 classes  
*   
* [Art Genome Project](https://www.artsy.net/categories)  
  * Art  
  * **Interesting attributes**  
    * Time Periods: 1000 \- 1400 CE Art, 18th Century Art, 1900 \- 1917 Art, etc  
    * Visual Qualities: Abstract Illusionism, Asymmetrical, Balance, etc  
    * …many others  
* [Jin2024](https://arxiv.org/pdf/2411.08545)  
  * Art  
  * **Interesting attributes**: Theme and Logic, Creativity, Layout and Composition, Space and Perspective, Sense of Order, Light and Shadow, Color, Details and Texture, The Overall, Mood  
* [CelebA](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)  
  * People  
  * **Interesting attributes**: 5\_o\_Clock\_Shadow Arched\_Eyebrows Attractive Bags\_Under\_Eyes Bald Bangs Big\_Lips Big\_Nose Black\_Hair Blond\_Hair Blurry Brown\_Hair Bushy\_Eyebrows Chubby Double\_Chin Eyeglasses Goatee Gray\_Hair Heavy\_Makeup High\_Cheekbones Male Mouth\_Slightly\_Open Mustache Narrow\_Eyes No\_Beard Oval\_Face Pale\_Skin Pointy\_Nose Receding\_Hairline Rosy\_Cheeks Sideburns Smiling Straight\_Hair Wavy\_Hair Wearing\_Earrings Wearing\_Hat Wearing\_Lipstick Wearing\_Necklace Wearing\_Necktie Young  
* [FACET](https://ai.meta.com/datasets/facet/)  
  * People  
  * **Interesting attributes**  
    * Demographic  
      * perceived gender presentation : All of the following annotations will given in a binary fashion: \[gender presentation masc, gender presentation non binary, gender presentation fem, gender presentation na\]  
      * perceived skin tone : Each annotators annotations are considered per MST in a binary fashion. Annotations from all annotators are summed into a single value per MST, so the value at MSTi may be greater than 1\. Values will be given for all of the following: \[skin tone 1, ..., skin tone 10, skin tone na\]  
      * perceived age group : all of the following annotations are included in a binary fashion: \[age presentation young, age presentation middle, age presentation older, age presentation na\]  
    * Additional  
      * hair color: \[hair color black, hair color red, hair color blonde, hair color brown, hair color colored, hair color grey, hair color na\]  
      * hair type: \[hair type wavy, hair type curly, hair type coily, hair type straight, hair type bald, hair type dreadlocks, hair type na\]  
      * other items: \[has eyewear, has headscarf, has tattoo, has cap, has facial hair, has mask\]  
* [**https://www.cs.columbia.edu/CAVE/databases/pubfig/**](https://www.cs.columbia.edu/CAVE/databases/pubfig/)  
  * 58,797 images of 200 people  
  * 65 describable visual traits such as gender, age, race, hair color  
*   
* **Animals with Attributes (AwA)**  
  * [https://cvml.ista.ac.at/AwA2/](https://cvml.ista.ac.at/AwA2/)  
  *    
  * [https://ieeexplore.ieee.org/document/8413121](https://ieeexplore.ieee.org/document/8413121)  
  * [https://ieeexplore.ieee.org/document/5206594](https://ieeexplore.ieee.org/document/5206594)  
  * [Original dataset](https://sci-hub.box/https://pubmed.ncbi.nlm.nih.gov/24457503/)  
  * 37322 images of 50 animals  
  * 85 numeric attribute  
  * The class annotations come from [https://collaborate.princeton.edu/en/publications/default-probability](https://collaborate.princeton.edu/en/publications/default-probability) and [https://dl.acm.org/doi/10.5555/1597538.1597600](https://dl.acm.org/doi/10.5555/1597538.1597600)   
* **Stanford Dogs Dataset**  
  * [http://vision.stanford.edu/aditya86/ImageNetDogs/](http://vision.stanford.edu/aditya86/ImageNetDogs/)  
  * Number of categories: 120  
  * Number of images: 20,580  
  * Annotations: Class labels, Bounding boxes  
* **PawsomeAuthority Dog Breeds Dataset**  
  * [https://pawsomeauthority.com/dog-breeds/dataset/](https://pawsomeauthority.com/dog-breeds/dataset/)   
  * Just metadata, no images  
  * structured, scientifically-backed dataset of dog breeds  
  * 60 breeds, 60 attributes each  
* [https://github.com/tmfilho/akcdata](https://github.com/tmfilho/akcdata)  
  * American Kennel Club  
  * Dogs  
  * 277 breeds  
  * 20 attributes  
* **dataset\_lfw**  
  * [https://inria.hal.science/inria-00321923v1](https://inria.hal.science/inria-00321923v1)  
  * For studying unconstrained face recognition problems (in which there is little control over parameters such as position, pose, lighting, background, camera quality)  
* **dataset\_taras\_dog\_breeds**  
  * [https://github.com/AtharvaTaras/Dog-Breeds-Dataset](https://github.com/AtharvaTaras/Dog-Breeds-Dataset)  
  * breeds recognized by the FCI (Fédération Cynologique Internationale)  
  * Contains 35 images for each breed  
  * Total 356 Breeds  
  * Aprroximate Size (Uncompressed) \- 5.32 GB  
  * Around 2-7% duplicates  
  * built by scraping dog images from Bing web search. Used the FCI as an index of pure breeds, and the names from this index served as search keywords for the web scraper

# **General notes about unlearning**

**Definition:**

* Process of removing certain data points or features from a trained ML model without affecting its performance  
* Modify models to exclude specific data points efficiently  
* Recalibration of ML models by selectively discarding specific data points, patterns, or predictions  
    
    
  **Reasons:**  
* Comply to GDPR’s right to erasure  
* Comply to copyright protection  
* Rectify biases  
* Correct obsolete information  
    
    
  **Methods:**  
* post-image ﬁltering  
  * bypassable  
* inference guidance  
  * bypassable  
* retraining with the curated dataset  
  * Expensive  
* model ﬁnetuning  
  * Moderate cost, good results  
  * When retraining NN, you can retrain only the final layer; you can use then methods used for unlearning in linear or logistic regression


[**GDPR’s article 17**](https://gdpr-info.eu/art-17-gdpr/)**: right to erasure**

* Conditions  
  * data is no longer necessary to the purposes for which they were collected/processed  
  * subject withdraws consent, and where there is no other legal ground for the processing  
  * there are no overriding legitimate grounds for the processing  
  * If the data was unlawfully processed, it can be deleted regardless of the conditions above?  
  * if the controller made the data public, he is still obliged to delete it as much as possible  
* exceptions  
  * exercising the right of freedom of expression  
  * compliance with a legal obligation which requires processing by Union or Member State law to which the controller is subject  
  * requried for the performance of a task carried out in the exercise of official authority  
  * for archiving purposes in the public interest, scientific or historical research  
  * for the establishment, exercise or defence of legal claims


  


  **Metrics:**

* Anamnesis Index  
  * This index measures how much information about the unlearned data remains within the model postunlearning  
  * evaluates whether the unlearned data can still influence the model’s outputs,  
* Model distance (calculate the layerwise distance between the original and the unlearned model)  
* JSdivergence: assess whether the unlearning process causes the model to alter its predictions significantly for situation outside the forget-set  
* Epistemic Uncertainty: quantifies the uncertainty in the model’s predictions postunlearning  
* variational forgetting assess the model’s ability to discard specific information or tasks  
* Measure quality metrics (precision, RMSE, etc) before and after unlearning  
* Measure fairness metrics before and after unlearning  
* membership inference attacks over the forget set  
* LiRa: [https://arxiv.org/abs/2112.03570](https://arxiv.org/abs/2112.03570) 


  **Datasets:**

* Ciphar-10  
* Ciphar-100  
* [Google’s unlearning challenge](https://ai.googleblog.com/2023/06/announcing-first-machine-unlearning.html)  
* [CelebA](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)  
  * Numered identities (no name)  
  * 10,177 number of identities,  
  * 202,599 number of face images  
  * 5 landmark locations, 40 binary attributes annotations per image  
* [FACET](https://ai.meta.com/datasets/facet/)  
  * 13 person-related attributes (e.g., perceived gender presentation, perceived skin tone, hairstyle) and 52 person-related classes (e.g., basketball player, doctor)  
  * 32K images  
  * diverse, high-resolution, privacy protecting  
  * No identities
