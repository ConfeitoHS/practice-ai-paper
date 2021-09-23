# Results

## Implementation

### Architecture

#### Generator

컨볼루션 레이어가 세 개이고 residual block이 몇 개 있는 네트워크 구조를 가진다.

컨볼루션 레이어 중 두 레이어는 fractionally strided convolution\(보통 ConvTranspose\)이고 나머지 하나는 결과를 RGB로 출력한다.

Residual block은 128x128 이미지에서 6개, 256x256 이미지에서 9개를 사용한다.

#### Discriminator

PatchGAN에 사용된 discriminator 구조를 사용한다. 70x70의 patch 크기를 가지는 모델이다.

{% hint style="success" %}
PatchGAN은 이미지 전체를 보고 하나의 T/F값을 내는 것이 아닌 window 내의 픽셀만 보고 이동하면서 여러개의 T/F값을 내는 discriminator를 사용한다. 따라서 파라미터 수가 줄어들며, discriminator를 속이기 위해 이미지 부분부분이 흐릿해지는 현상이 해결된다.
{% endhint %}

### Training

GAN의 학습은 매우 불안정하다. Generator에 비해 discriminator의 파라미터는 상대적으로 적기 때문에 discriminator의 학습이 쉬우며 불안정하고 generator또한 영향을 받는다. 이를 해결하기 위해 여러 안정화 방법이 사용된다. 학습의 안정화를 위해 CycleGAN에서는 다음 두 방법을 사용한다.

앞에서 설명한 loss function은 음의 로그 가능도였지만 학습의 안정화를 위해 least-square loss\(최소제곱, LSGAN에서 사용\)를 사용한다. Generator와 Discriminator에 적용되는 loss를 식으로 나타내면

$$
G: \mathbb E_{x\sim p_{data}(x)}[(D(G(x))-1)^2] \qquad D:\mathbb E_{y\sim p_{data}(y)}[(D(y)-1)^2]+ \mathbb E_{x\sim p_{data}(x)}[D(G(x))^2]
$$

Generator는 discriminator가 1을 만들도록 학습하며 Discriminator는 올바르게 구분할 수 있도록 최소화한다는 점은 같다.

또, 학습 곡선의 안정화를 위해 이전에 generator가 생성한 50개의 이미지를 버퍼\(replay buffer\)에 저장, 이를 이용해 discriminator를 50개의 이미지로 업데이트한다. 

Adam optimizer에 0.0002의 learning rate를 사용하고 cycle consistency loss의 가중치는 $$\lambda = 10$$으로 한다. Batch size=1이고 100epoch 이후에는 lr을 decay한다.

## Results

모든 결과를 표시하진 않고, CycleGAN의 목적을 이해하는 데 핵심적인 결과만 본다.

### Ablation

![](../.gitbook/assets/image%20%2826%29.png)

논문에서 CycleGAN의 일부 구조를 제거\(ablation, 절제\)하며 loss function을 분석한다. GAN loss와 cycle consistency loss를 각각 없애면 성능이 크게 줄어든다. 두 loss모두 성능에 결정적인 영향을 미치는 것으로 판단했다. 한쪽 방향의 cycle consistency loss를 없앴을 때, mode collapse가 나타났다고 한다. 

### Identity loss

![](../.gitbook/assets/image%20%2825%29.png)

연구진은 style transfer과 같은 task에서 identity loss를 추가했다.[ 앞에서](formulation.md#additional-loss-identity-loss) 설명한 것 처럼 loss는 다음과 같다.

$$
\mathcal L_{identity}(G,F)=\mathbb E_{x\sim p_{data}(x)}[\| F(x)-x \|_1]+\mathbb E_{y\sim p_{data}(y)}[\| G(y)-y \|_1]
$$

도메인 변환 시, identity loss가 없다면 generator가 색감을 완전히 바꾸어도 충분히 최적화된다.  GAN loss는 서로를 속이는 것에 대한 loss고, cycle consistency loss는 왕복 복원에 대한 loss기 때문에 한 도메인에서 다른 도메인으로 변환된 후 색감을 바꾸어 버려도 매우 잘 최적화된다. 따라서 두 도메인의 차이를 줄여주는 constrain을 건다.
