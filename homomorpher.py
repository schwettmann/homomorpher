
!git clone https://github.com/schwettmann/pretorched-x.git
cd /content/pretorched-x
!pip install torchaudio
#

import functools
import torch
from pretorched import gans
from pretorched.gans import BigGAN, biggan, utils
from pretorched import visualizers as vutils

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

res = 256
batch_size = 30
pretrained = 'places365'
n_classes = {'places365': 365, 'imagenet': 1000}.get(pretrained)
class_idx = 205    #lake with trees 
G = BigGAN(resolution=res, pretrained=pretrained, load_ema=True).to(device)

g = functools.partial(G, embed=True)
batch_size = 1
z, _ = utils.prepare_z_y(batch_size, G.dim_z, n_classes, device=device, z_var=0.5)  #generate random z, do this multiple times to find z you like 

def generate_img(z, class_idx):    #for some z and some class (in Places365), generates image
	y = class_idx * torch.ones(batch_size, device=device).long()
	with torch.no_grad():
    	G_z = utils.elastic_gan(g, z, y)  # Allows for batches larger than what fits in memory.  
	vutils.visualize_samples(G_z)         # Visualizes the image 
	return G_z  

def transform_img(z, class_idx, svm_lbl):  #from z + orig category, name of SVM to use; return original image and transformed image
	#svm_lbl can be SVM_lakereeflection or SVM_summerlakes
	y = class_idx * torch.ones(batch_size, device=device).long()
	with torch.no_grad():
    	G_z = utils.elastic_gan(g, z, y)  # Allows for batches larger than what fits in memory.  
  current_z = torch.nn.Parameter(z, requires_grad=True)   #makes space to hold gradients - z is the kind of thing we can optimize   
	parameters = [current_z]   #yes we are still shifting z, this time based on the SVM value. 
	num_steps =500   #sure
	optimizer = torch.optim.Adam([current_z])    
	loss_vec= []	

	def elastic_gan_with_grad(model, *input):
    	error_msg = 'CUDA out of memory.'

    	def chunked_forward(f, *x, chunk_size=1):
        	out = []
        	for xcs in zip(*[xc.chunk(chunk_size) for xc in x]):
            	o = f(*xcs)
            	out.append(o)
        	return torch.cat(out)

    	cs, fit = 1, False
    	while not fit:
        	try:
            	return chunked_forward(model, *input, chunk_size=cs)
        	except RuntimeError as e:
            	if error_msg in str(e):
                	torch.cuda.empty_cache()
                	cs *= 2
            	else:
                	raise e
    
  !git clone https://github.com/schwettmann/homomorpher.git
	path = "/content/pretorched-x/homomorpher/SVMs/{svm_lbl}"
	model = torch.load(path)
	model.eval()

    with torch.enable_grad():
    	for step_num in (range(num_steps + 1)):
    		optimizer.zero_grad()
    		outputs = model(current_z) 
    		loss = -model(current_z)   # flip this sign to change direction across the decision boundary 
    		loss_vec.append(loss)
    		loss.backward()
    		optimizer.step()

    G_z2 = utils.elastic_gan(g, current_z, y)  # generate transformed image 
    vutils.visualize_samples(G_z) 
    vutils.visualize_samples(G_z2) 
    return G_z, G_z2






