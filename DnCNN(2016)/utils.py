import torch 
import numpy as np 
from PIL import Image
from torchvision import transforms
import torch.nn as nn

def calc_psnr(i1,i2):
    p = 0.
    p= -10*torch.log10(torch.mean((i1[0,:,:]-i2[0,:,:])**2))
    return p.item()

def calc_psnr_rgb(i1,i2):
    p = 0.
    p+= -10*torch.log10(torch.mean((i1[0,:,:]-i2[0,:,:])**2))
    p+= -10*torch.log10(torch.mean((i1[1,:,:]-i2[1,:,:])**2))
    p+= -10*torch.log10(torch.mean((i1[2,:,:]-i2[2,:,:])**2))
    return (p/3.).item()

def calc_ssim(i1,i2):
    c1= 0.01**2
    c2= 0.03**2
    c3=c2/2
    
    m1 = torch.mean(i1)
    m2 = torch.mean(i2)
    s1 = torch.std(i1)
    s2 = torch.std(i2)
    cov = torch.dot((i1-m1).view(-1),(i2-m2).view(-1)) / (i1.numel()-1)
    return ((2*m1*m2+c1)*(2*cov+c2)/(m1**2+m2**2+c1)/(s1**2+s2**2+c2)).item()

def conv_init(m):
    t = type(m)
    if m == nn.Conv2d:
        nn.init.kaiming_normal(m.weight.data, a=0, mode='fan_in')
    elif m == nn.Linear:
        nn.init.kaiming_normal(m.weight.data, a=0, mode='fan_in')
    elif m == nn.BatchNorm2d:
        m.weight.data.normal_(mean=0, std=nn.math.sqrt(2./9./64.)).clamp_(-0.025,0.025)
        nn.init.constant(m.bias.data, 0.0)