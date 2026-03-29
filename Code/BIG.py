import os
import zipfile
import shutil
from google.colab import drive

DRIVE_ZIP_PATH = '/content/drive/MyDrive/breast_blaster/init_dataset/init_data.zip'

LOCAL_WORKDIR = '/content/breast_data'
ZIP_LOCAL = '/content/init_data.zip'

if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

if os.path.exists(LOCAL_WORKDIR):
    shutil.rmtree(LOCAL_WORKDIR)
os.makedirs(LOCAL_WORKDIR, exist_ok=True)

print(f"📦 Copia dello ZIP in corso...")
if os.path.exists(DRIVE_ZIP_PATH):
    shutil.copy(DRIVE_ZIP_PATH, ZIP_LOCAL)
    print("✅ Copia completata.")
else:
    raise FileNotFoundError(f"❌ Errore: File non trovato su Drive al percorso: {DRIVE_ZIP_PATH}")

print(f"📂 Estrazione in corso in {LOCAL_WORKDIR}...")
with zipfile.ZipFile(ZIP_LOCAL, 'r') as zip_ref:
    zip_ref.extractall(LOCAL_WORKDIR)
print("✅ Estrazione completata.")

def check_structure(base_path):
    print("\n🔍 Verifica struttura cartelle:")
    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/ (file: {len(files)})")

check_structure(LOCAL_WORKDIR)

os.remove(ZIP_LOCAL)

print("Tutto Pronto!")

"""Cleaning MacOS garbage in zip"""

import os
import shutil

base_path = '/content/breast_data'
extra_folder = os.path.join(base_path, 'init_data')
macosx_folder = os.path.join(base_path, '__MACOSX')

print("🧹 Inizio pulizia dataset...")

if os.path.exists(macosx_folder):
    shutil.rmtree(macosx_folder)
    print("✅ Cartella __MACOSX rimossa.")

if os.path.exists(extra_folder):
    for item in os.listdir(extra_folder):
        s = os.path.join(extra_folder, item)
        d = os.path.join(base_path, item)
        if os.path.exists(d):
            if os.path.isdir(d): shutil.rmtree(d)
            else: os.remove(d)
        shutil.move(s, d)

    shutil.rmtree(extra_folder)
    print("✅ Contenuto spostato e cartella init_data rimossa.")

print("\n✨ Struttura finale pulita:")
for root, dirs, files in os.walk(base_path):
    level = root.replace(base_path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    if level <= 2:
        print(f"{indent}{os.path.basename(root)}/ (file: {len(files)})")

csv_found = any(f.endswith('.csv') for f in os.listdir(base_path))
if csv_found:
    print("\n📝 dataset.csv trovato nella root di breast_data.")
else:
    print("\n⚠️ Attenzione: dataset.csv non trovato nella root!")

"""Visual sanity check on masks position and preprocessing success"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os
import numpy as np

CSV_PATH = '/content/breast_data/dataset.csv'
IMAGES_BASE_DIR = '/content/breast_data/images'
NUM_SAMPLES = 10

def visual_sanity_check(csv_path, images_dir, n_samples=10):
    df = pd.read_csv(csv_path)

    df_lesions = df[df['No_Finding'] == 0].dropna(subset=['new_xmin', 'new_ymin', 'new_xmax', 'new_ymax'])

    unique_ids = df_lesions['image_id'].unique()
    if len(unique_ids) < n_samples:
        n_samples = len(unique_ids)

    selected_ids = np.random.choice(unique_ids, n_samples, replace=False)

    fig, axes = plt.subplots(2, 5, figsize=(20, 10))
    axes = axes.flatten()

    print(f"🔍 Visualizzazione di {n_samples} campioni con lesioni...")

    for i, img_id in enumerate(selected_ids):
        img_info = df[df['image_id'] == img_id].iloc[0]
        split = img_info['split']
        img_path = os.path.join(images_dir, split, img_id)

        if not os.path.exists(img_path):
            axes[i].text(0.5, 0.5, f"Missing:\n{img_id}", ha='center')
            axes[i].axis('off')
            continue

        img = Image.open(img_path).convert('RGB')
        axes[i].imshow(img)

        boxes = df_lesions[df_lesions['image_id'] == img_id]

        for _, box in boxes.iterrows():
            xmin, ymin, xmax, ymax = box['new_xmin'], box['new_ymin'], box['new_xmax'], box['new_ymax']

            rect = patches.Rectangle(
                (xmin, ymin), xmax - xmin, ymax - ymin,
                linewidth=2, edgecolor='lime', facecolor='none'
            )
            axes[i].add_patch(rect)

            label = "Lesion"
            if box['Mass'] == 1: label = "Mass"
            elif box['Suspicious_Calcification'] == 1: label = "Calc"

            axes[i].text(xmin, ymin - 5, label, color='lime', fontsize=9, fontweight='bold',
                         bbox=dict(facecolor='black', alpha=0.5, lw=0))

        axes[i].set_title(f"ID: {img_id[:8]}... | {split.upper()}", fontsize=10)
        axes[i].axis('off')

    plt.tight_layout()
    plt.show()

visual_sanity_check(CSV_PATH, IMAGES_BASE_DIR, n_samples=NUM_SAMPLES)

"""Saving clean"""

import os
import shutil
import zipfile
from tqdm import tqdm

base_path = '/content/breast_data'
macosx_folder = os.path.join(base_path, '__MACOSX')
drive_out_dir = '/content/drive/MyDrive/breast_blaster/ready_data'
zip_out_name = os.path.join(drive_out_dir, 'data_pro')

print("🧹 Inizio pulizia profonda...")

if os.path.exists(macosx_folder):
    shutil.rmtree(macosx_folder)
    print("✅ Cartella __MACOSX rimossa.")

print("🔍 Ricerca e rimozione file corrotti ._ ...")
removed_files = 0
for root, dirs, files in os.walk(base_path):
    for f in files:
        if f.startswith('._') or f == '.DS_Store':
            os.remove(os.path.join(root, f))
            removed_files += 1
if removed_files > 0:
    print(f"✅ Rimossi {removed_files} file di sistema macOS.")

os.makedirs(drive_out_dir, exist_ok=True)

print(f"📦 Creazione dello ZIP pulito in {zip_out_name}.zip ...")
try:
    shutil.make_archive(zip_out_name, 'zip', base_path)
    print(f"✅ Archivio salvato con successo su Drive!")
except Exception as e:
    print(f"❌ Errore durante la creazione dello ZIP: {e}")

zip_full_path = zip_out_name + '.zip'
if os.path.exists(zip_full_path):
    size_gb = os.path.getsize(zip_full_path) / (1024**3)
    print(f"📊 Dimensione finale dello ZIP: {size_gb:.2f} GB")

"""## Dataset and Dataloader

Setup
"""

import os
import shutil
import zipfile
import numpy as np
import pandas as pd
from google.colab import drive

if not os.path.exists("/content/drive"):
    drive.mount("/content/drive")

DRIVE_PATH = "/content/drive/MyDrive/breast_blaster/ready_data/data_pro.zip"
LOCAL_PATH = "/content/breast_data"
ZIP_LOCAL = "/content/temp_dataset.zip"

"""Dataset loading"""

import os
import shutil
import zipfile
import numpy as np
import pandas as pd
from google.colab import drive

if not os.path.exists("/content/drive"):
    drive.mount("/content/drive")

DRIVE_PATH = "/content/drive/MyDrive/breast_blaster/ready_data/data_pro.zip"
LOCAL_PATH = "/content/breast_data"
ZIP_LOCAL = "/content/temp_dataset.zip"

if os.path.exists(LOCAL_PATH):
    shutil.rmtree(LOCAL_PATH)
os.makedirs(LOCAL_PATH, exist_ok=True)

print(f"📦 Copia del dataset in corso...")
if os.path.exists(DRIVE_PATH):
    shutil.copy(DRIVE_PATH, ZIP_LOCAL)
    with zipfile.ZipFile(ZIP_LOCAL, 'r') as zip_ref:
        zip_ref.extractall(LOCAL_PATH)
    os.remove(ZIP_LOCAL)
    print("✅ Estrazione completata con successo.")
else:
    raise FileNotFoundError(f"❌ Errore: File non trovato in {DRIVE_PATH}")

CSV_PATH = os.path.join(LOCAL_PATH, "dataset.csv")

if os.path.exists(CSV_PATH):
    print(f"📝 Caricamento metadati da: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)

    df['image_id'] = df['image_id'].astype(str).str.replace('.png', '', regex=False)

    df_unique = df.drop_duplicates('image_id').copy()

    contra_map = {}
    for _, row in df_unique.iterrows():
        key = (row['patient_id'], row['view'])
        if key not in contra_map:
            contra_map[key] = {}
        contra_map[key][row['laterality']] = row['image_id']

    print(f"✅ Setup completato. Immagini totali: {len(df_unique)}")
    print(f"📊 Distribuzione split:\n{df_unique['split'].value_counts()}")
else:
    print(f"⚠️ Errore: 'dataset.csv' non trovato nella root dell'archivio!")

"""Dataset and Dataloader definition and initialization for **VAE**"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import os
from PIL import Image

class BreastDataset(Dataset):
    def __init__(self, split="train", df=None, contra_map=None):
        self.split = split
        self.base_path = f"/content/breast_data/images/{split}"

        self.split_df = df[df['split'] == split].copy()

        self.split_df['image_id_clean'] = self.split_df['image_id'].astype(str).str.replace('.png', '', regex=False)
        self.ids = self.split_df['image_id_clean'].unique().tolist()

        self.meta_df = self.split_df.drop_duplicates('image_id_clean').set_index('image_id_clean')
        self.contra_map = contra_map

        print(f"🧠 Caricamento {split.upper()} in RAM ({len(self.ids)} immagini)...")
        self.images_cache = {}

        missing_count = 0
        for img_id in self.ids:
            potential_names = [f"{img_id}.png", img_id]
            img_found = False

            for name in potential_names:
                img_path = os.path.join(self.base_path, name)
                if os.path.exists(img_path):
                    with Image.open(img_path) as img:
                        img_np = np.array(img.convert('L'), dtype=np.float32) / 255.0
                        self.images_cache[img_id] = img_np
                    img_found = True
                    break

            if not img_found:
                missing_count += 1

        if missing_count > 0:
            print(f"⚠️ Attenzione: {missing_count} immagini non trovate in {self.base_path}")
        else:
            print(f"✅ Tutte le {len(self.ids)} immagini caricate correttamente.")

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        img_id = self.ids[idx]
        img_np = self.images_cache[img_id]

        img = torch.from_numpy(img_np).unsqueeze(0)
        img = (img * 2.0) - 1.0

        row = self.meta_df.loc[img_id]

        mass = float(row['Mass'])
        calc = float(row['Suspicious_Calcification'])
        density = float(row['density']) / 3.0
        condition = torch.tensor([mass, calc, density], dtype=torch.float32)

        bbox = torch.tensor([
            float(row.get('new_xmin', 0.0)),
            float(row.get('new_ymin', 0.0)),
            float(row.get('new_xmax', 0.0)),
            float(row.get('new_ymax', 0.0))
        ], dtype=torch.float32)

        p_id = row['patient_id']
        view = row['view']
        side = row['laterality']
        other_side = 'R' if side == 'L' else 'L'

        contra_id_raw = self.contra_map.get((p_id, view), {}).get(other_side)

        contra_id = str(contra_id_raw).replace('.png', '') if contra_id_raw else None

        if contra_id and contra_id in self.images_cache:
            contra_img_np = self.images_cache[contra_id]
            contra_img = torch.from_numpy(contra_img_np).unsqueeze(0)
            contra_img = (contra_img * 2.0) - 1.0
        else:
            contra_img = torch.flip(img, [2])

        return {
            "image": img,
            "contralateral": contra_img,
            "condition": condition,
            "bbox": bbox,
            "img_id": img_id
        }

train_ds = BreastDataset("train", df, contra_map)
val_ds   = BreastDataset("val", df, contra_map)
test_ds  = BreastDataset("test", df, contra_map)

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0, pin_memory=True)
val_loader   = DataLoader(val_ds, batch_size=32, shuffle=False, num_workers=0, pin_memory=True)
test_loader  = DataLoader(test_ds, batch_size=32, shuffle=False)

print(f"\n🚀 Dataloaders pronti. RAM occupata stimata: {len(df)*512*512*4 / (1024**2):.2f} MB")

"""Numerical and visual sanity check"""

import matplotlib.pyplot as plt
import numpy as np

def check_dataloader_v2(loader):

    batch = next(iter(loader))
    imgs = batch["image"]
    contras = batch["contralateral"]
    boxes = batch["bbox"]
    conds = batch["condition"]

    print(f"✅ Batch caricato!")
    print(f"Shape Immagini: {imgs.shape}")
    print(f"Shape Condizioni: {conds.shape} -> [Mass, Calc, Density]")

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))

    for i in range(min(4, imgs.shape[0])):
        img_vis = (imgs[i][0].cpu().numpy() + 1.0) / 2.0
        axes[0, i].imshow(img_vis, cmap='gray')

        box = boxes[i].cpu().numpy()
        if box[2] > 0:
            rect = plt.Rectangle((box[0], box[1]), box[2]-box[0], box[3]-box[1],
                                 fill=False, color='lime', linewidth=2, label='BBox')
            axes[0, i].add_patch(rect)
            mask_overlay = np.zeros_like(img_vis)
            mask_overlay[int(box[1]):int(box[3]), int(box[0]):int(box[2])] = 1.0
            axes[0, i].imshow(mask_overlay, cmap='Reds', alpha=0.3)

        m, c, d = conds[i].cpu().numpy()
        axes[0, i].set_title(f"TARGET\nMass:{int(m)} | Calc:{int(c)} | Dens:{d:.2f}")
        axes[0, i].axis('off')

        contra_vis = (contras[i][0].cpu().numpy() + 1.0) / 2.0
        axes[1, i].imshow(contra_vis, cmap='gray')

        axes[1, i].set_title("Anatomical Reference\n(Contralateral)")
        axes[1, i].axis('off')

    plt.tight_layout()
    plt.show()

check_dataloader_v2(test_loader)

"""## VAE

Setup
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install lpips

import os
import torch
import numpy as np
import random
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from google.colab import drive

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

PROJECT_ROOT = "/content/drive/MyDrive/breast_blaster"
READY_DATA_DIR = os.path.join(PROJECT_ROOT, "ready_data")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

LOCAL_DATA = "/content/breast_data"

os.makedirs(MODELS_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"✅ Setup pronto su {DEVICE}")
print(f"📂 Root Progetto: {PROJECT_ROOT}")
print(f"📂 Directory Modelli: {MODELS_DIR}")

try:
    print(f"✅ Dataloaders pronti!")
except NameError:
    print("⚠️ Attenzione: I Dataloader non sono ancora stati definiti in questa sessione.")

"""Variational Autoencoder (**VAE**) class"""

import torch
import torch.nn as nn
import torch.nn.functional as F

checkpoint_path      = os.path.join(MODELS_DIR, "vae_f8_c4_EMERGENCY_STOP.pth")
disc_checkpoint_path = os.path.join(MODELS_DIR, "disc_f8_c4_EMERGENCY_STOP.pth")
best_model_save_path = os.path.join(MODELS_DIR, "vae_f8_c4_best.pth")

class ResBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(c, c, 3, padding=1),
            nn.GroupNorm(min(32, c), c),
            nn.SiLU(),
            nn.Conv2d(c, c, 3, padding=1),
            nn.GroupNorm(min(32, c), c)
        )
    def forward(self, x):
        return x + self.block(x)

class Encoder(nn.Module):
    def __init__(self, in_ch=1, base=64, latent_ch=4):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Sequential(nn.Conv2d(in_ch, base,    4, 2, 1), ResBlock(base)),
            nn.Sequential(nn.Conv2d(base,   base*2, 4, 2, 1), ResBlock(base*2)),
            nn.Sequential(nn.Conv2d(base*2, base*4, 4, 2, 1), ResBlock(base*4)),
        ])
        self.mu     = nn.Conv2d(base*4, latent_ch, 3, padding=1)
        self.logvar = nn.Conv2d(base*4, latent_ch, 3, padding=1)

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return self.mu(x), self.logvar(x)

class Decoder(nn.Module):
    def __init__(self, out_ch=1, base=64, latent_ch=4):
        super().__init__()
        self.up = nn.ModuleList([
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                nn.Conv2d(latent_ch, base*4, 3, padding=1),
                ResBlock(base*4)
            ),
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                nn.Conv2d(base*4, base*2, 3, padding=1),
                ResBlock(base*2)
            ),
            nn.Sequential(
                nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False),
                nn.Conv2d(base*2, base, 3, padding=1),
                ResBlock(base)
            ),
        ])
        self.final = nn.Conv2d(base, out_ch, 3, padding=1)

    def forward(self, z):
        x = z
        for layer in self.up:
            x = layer(x)
        return torch.tanh(self.final(x))

class ResidualVAE(nn.Module):
    def __init__(self, in_ch=1, base=64, latent_ch=4):
        super().__init__()
        self.enc = Encoder(in_ch, base, latent_ch)
        self.dec = Decoder(in_ch, base, latent_ch)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar.clamp(-6, 6))
        return mu + std * torch.randn_like(std)

    def forward(self, x):
        mu, logvar = self.enc(x)
        z = self.reparameterize(mu, logvar)
        return self.dec(z), mu, logvar

model = ResidualVAE(base=64, latent_ch=4).to(DEVICE)

if os.path.exists(checkpoint_path):
    print("♻️ Checkpoint VAE trovato, caricamento...")
    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location=DEVICE))
        print("✅ Pesi VAE caricati.")
    except Exception as e:
        print(f"⚠️ Errore: {e} — inizializzazione da zero.")
        with torch.no_grad():
            model.enc.logvar.bias.data.fill_(0.1)
else:
    print("🆕 Inizializzazione da zero.")
    with torch.no_grad():
        model.enc.logvar.bias.data.fill_(0.1)

print(f"📊 VAE latent: [B, 4, 64, 64] | DEVICE: {DEVICE}")

"""Composed loss definition"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import spectral_norm
import lpips

class Discriminator(nn.Module):
    def __init__(self, in_ch=1, base=8):
        super().__init__()
        def sn(in_f, out_f, k, s, p):
            return spectral_norm(nn.Conv2d(in_f, out_f, k, s, p))
        self.main = nn.Sequential(
            sn(in_ch, base,    4, 2, 1), nn.LeakyReLU(0.2, inplace=True),
            sn(base,   base*2, 4, 2, 1), nn.InstanceNorm2d(base*2, affine=True), nn.LeakyReLU(0.2, inplace=True),
            sn(base*2, base*4, 4, 2, 1), nn.InstanceNorm2d(base*4, affine=True), nn.LeakyReLU(0.2, inplace=True),
            sn(base*4, 1,      4, 1, 1)
        )
    def forward(self, x):
        return self.main(x)

loss_fn_lpips = lpips.LPIPS(net='alex').to(DEVICE)
loss_fn_lpips.requires_grad_(False)

def compute_lpips(x, x_hat):
    return loss_fn_lpips(x.repeat(1,3,1,1), x_hat.repeat(1,3,1,1)).mean()

def compute_gdl(x, x_hat):
    dy_t = torch.abs(x[:,:,1:,:]     - x[:,:,:-1,:])
    dy_p = torch.abs(x_hat[:,:,1:,:] - x_hat[:,:,:-1,:])
    dx_t = torch.abs(x[:,:,:,1:]     - x[:,:,:,:-1])
    dx_p = torch.abs(x_hat[:,:,:,1:] - x_hat[:,:,:,:-1])
    return torch.mean((dy_t-dy_p)**2) + torch.mean((dx_t-dx_p)**2)

_laplacian_kernel = torch.tensor(
    [[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=torch.float32
).view(1, 1, 3, 3)

def compute_hf_loss(x, x_hat):
    kernel  = _laplacian_kernel.to(x.device)
    hf_x    = F.conv2d(x.float(),     kernel, padding=1)
    hf_xhat = F.conv2d(x_hat.float(), kernel, padding=1)
    return F.l1_loss(hf_xhat, hf_x)

def vae_loss_engine(x, x_hat, mu, logvar, d_fake, current_step, config):
    l1_loss  = F.l1_loss(x_hat, x)   * config['w_l1']
    lpips_l  = compute_lpips(x, x_hat) * config['w_lpips']
    gdl_loss = compute_gdl(x, x_hat)  * config['w_gdl']
    hf_loss  = compute_hf_loss(x, x_hat) * config['w_hf']

    logvar_c  = logvar.clamp(-6, 6)
    kl_elem   = -0.5 * (1 + logvar_c - mu.pow(2) - logvar_c.exp())
    kl_per_ch = kl_elem.mean(dim=[0, 2, 3])
    kl_free   = torch.clamp(kl_per_ch, min=config['free_bits']).mean()
    kl_w      = min(config['kl_target'],
                    config['kl_target'] * (current_step / config['kl_warmup_steps']))

    adv_loss = torch.tensor(0.0, device=x.device)
    if current_step > config['gan_warmup']:
        adv_loss = -torch.mean(d_fake) * config['w_adv']

    total = l1_loss + lpips_l + gdl_loss + hf_loss + (kl_free * kl_w) + adv_loss
    return total, l1_loss, lpips_l, gdl_loss, hf_loss, adv_loss, kl_w

def discriminator_loss(d_real, d_fake):
    return 0.5 * (
        torch.mean(F.relu(1.0 - d_real)) +
        torch.mean(F.relu(1.0 + d_fake))
    )

model_disc = Discriminator(base=8).to(DEVICE)
print("✅ Loss engine | L1+LPIPS+GDL+HF | KL=1e-6 | no focal")

"""Warning suppression"""

import warnings
import logging
import torch

warnings.filterwarnings("ignore", category=UserWarning, message="The given NumPy array is not writable")
warnings.filterwarnings("ignore", category=UserWarning, message="Please use the new API settings to control TF32 behavior")
warnings.filterwarnings("ignore", category=UserWarning, message="The parameter 'pretrained' is deprecated")

print("✅ Warning soppressi  correttamente.")

"""Evalutation functions"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import torch
from tqdm import tqdm
import numpy as np

#scaling factor function
@torch.no_grad()
def calculate_vae_scaling_factor(model, dataloader, device):
    model.eval()
    all_mus = []

    print("⏳ Estrazione dei latenti per il calcolo dello scaling factor...")
    for batch in tqdm(dataloader):
        x = batch["image"].to(device)

        mu, _ = model.enc(x)

        all_mus.append(mu.cpu())

    all_mus = torch.cat(all_mus, dim=0)

    latent_std = all_mus.std().item()
    latent_mean = all_mus.mean().item()

    scale_factor = 1.0 / latent_std

    print("\n" + "="*50)
    print(f"📊 ANALISI SPAZIO LATENTE (f=8, ch=8)")
    print(f"  > Media globale:     {latent_mean:.6f}")
    print(f"  > Dev. Std (sigma):  {latent_std:.6f}")
    print(f"  > Varianza (sigma²): {latent_std**2:.6f}")
    print("-" * 50)
    print(f"💎 SCALING FACTOR DA USARE: {scale_factor:.6f}")
    print("="*50)

    print(f"\n💡 Istruzioni per il Diffusion Model:")
    print(f"   Durante il training del Denoiser, moltiplica i latenti così:")
    print(f"   latents = encoder_mu * {scale_factor:.6f}")

    return scale_factor

#lesions reconstruction evaluation and ratio between masses and calcification
@torch.no_grad()
def diagnose_lesion_quality(model, dataloader, device, n=20):
    model.eval()
    mass_l1s, calc_l1s = [], []

    for batch in dataloader:
        x          = batch["image"].to(device)
        conditions = batch["condition"]
        bboxes     = batch["bbox"]

        x_hat, _, _ = model(x)

        for i in range(len(x)):
            has_mass = conditions[i][0].item() == 1.0
            has_calc = conditions[i][1].item() == 1.0
            bbox     = bboxes[i]

            if bbox.sum() == 0:
                continue

            scale = x.shape[-1] / 512.0
            x0 = max(int(bbox[0].item() * scale), 0)
            y0 = max(int(bbox[1].item() * scale), 0)
            x1 = min(int(bbox[2].item() * scale), x.shape[-1])
            y1 = min(int(bbox[3].item() * scale), x.shape[-2])

            if x1 <= x0 or y1 <= y0:
                continue

            crop_orig = x[i:i+1, :, y0:y1, x0:x1]
            crop_hat  = x_hat[i:i+1, :, y0:y1, x0:x1]
            l1_crop   = F.l1_loss(crop_hat, crop_orig).item()

            if has_calc:
                calc_l1s.append(l1_crop)
            elif has_mass:
                mass_l1s.append(l1_crop)

        if len(mass_l1s) >= n and len(calc_l1s) >= n:
            break

    print(f"📊 Qualità per tipo di lesione (zona bbox):")
    print(f"   Masse         L1: {sum(mass_l1s)/len(mass_l1s):.5f} ({len(mass_l1s)} campioni)")
    print(f"   Calcificazioni L1: {sum(calc_l1s)/len(calc_l1s):.5f} ({len(calc_l1s)} campioni)")

    ratio = (sum(calc_l1s)/len(calc_l1s)) / (sum(mass_l1s)/len(mass_l1s))
    print(f"   Ratio calc/mass: {ratio:.2f}x")
    if ratio > 2.0:
        print("   ⚠️ Limite architetturale — le calc sono troppo piccole per 64x64")
    elif ratio > 1.3:
        print("   ⚠️ Margine di miglioramento con più training")
    else:
        print("   ✅ Qualità comparabile tra masse e calcificazioni")


#visual evauation
@torch.no_grad()
def visualize_reconstruction_v4(model, dataloader, device, epoch,
                                  n_mass=2, n_calc=3):
    model.eval()

    mass_samples = []
    calc_samples = []

    for batch in dataloader:
        conditions = batch["condition"]
        for i in range(len(conditions)):
            has_mass = conditions[i][0].item() == 1.0
            has_calc = conditions[i][1].item() == 1.0
            if has_mass and len(mass_samples) < n_mass:
                mass_samples.append({
                    "image": batch["image"][i],
                    "bbox":  batch["bbox"][i],
                    "label": "MASSA"
                })
            elif has_calc and not has_mass and len(calc_samples) < n_calc:
                calc_samples.append({
                    "image": batch["image"][i],
                    "bbox":  batch["bbox"][i],
                    "label": "CALCIFICAZIONE"
                })
        if len(mass_samples) >= n_mass and len(calc_samples) >= n_calc:
            break

    if len(calc_samples) < n_calc:
        for batch in dataloader:
            conditions = batch["condition"]
            for i in range(len(conditions)):
                if conditions[i][1].item() == 1.0 and len(calc_samples) < n_calc:
                    calc_samples.append({
                        "image": batch["image"][i],
                        "bbox":  batch["bbox"][i],
                        "label": "CALC(mixed)"
                    })
            if len(calc_samples) >= n_calc:
                break

    samples = mass_samples + calc_samples
    n = len(samples)

    fig, axes = plt.subplots(n, 4, figsize=(20, 5 * n))
    if n == 1:
        axes = axes.reshape(1, -1)

    col_titles = ["Originale", "Ricostruzione", "Errore (|diff|)", "Zoom Lesione"]
    for j, t in enumerate(col_titles):
        axes[0, j].set_title(t, fontsize=12, fontweight='bold')

    colors = {'MASSA': 'lime', 'CALCIFICAZIONE': 'yellow', 'CALC(mixed)': 'orange'}

    for i, s in enumerate(samples):
        x     = s["image"].unsqueeze(0).to(device)
        bbox  = s["bbox"]
        label = s["label"]
        color = colors.get(label, 'cyan')

        x_hat, _, _ = model(x)
        x_vis     = (x[0, 0].cpu()     + 1.0) / 2.0
        x_hat_vis = (x_hat[0, 0].cpu() + 1.0) / 2.0
        diff_vis  = torch.abs(x_vis - x_hat_vis)

        axes[i, 0].imshow(x_vis,     cmap='gray')
        axes[i, 1].imshow(x_hat_vis, cmap='gray')
        axes[i, 2].imshow(diff_vis,  cmap='hot')

        if bbox.sum() > 0:
            rect = Rectangle(
                (bbox[0], bbox[1]), bbox[2]-bbox[0], bbox[3]-bbox[1],
                linewidth=2, edgecolor=color, facecolor='none'
            )
            axes[i, 0].add_patch(rect)

            cx = int((bbox[0] + bbox[2]) / 2)
            cy = int((bbox[1] + bbox[3]) / 2)
            y1, y2 = max(0, cy-64), min(512, cy+64)
            x1, x2 = max(0, cx-64), min(512, cx+64)
            zoom = x_hat_vis.numpy()[y1:y2, x1:x2]
            axes[i, 3].imshow(zoom, cmap='gray')

            bx0 = max(int(bbox[0]) - max(0, cx-64), 0)
            by0 = max(int(bbox[1]) - max(0, cy-64), 0)
            bx1 = min(int(bbox[2]) - max(0, cx-64), x2-x1)
            by1 = min(int(bbox[3]) - max(0, cy-64), y2-y1)
            if bx1 > bx0 and by1 > by0:
                rect_z = Rectangle(
                    (bx0, by0), bx1-bx0, by1-by0,
                    linewidth=1.5, edgecolor=color, facecolor='none'
                )
                axes[i, 3].add_patch(rect_z)
        else:
            axes[i, 3].text(0.5, 0.5, "No BBox", ha='center', va='center')

        axes[i, 0].set_ylabel(label, fontsize=11, fontweight='bold', color=color)
        for j in range(4):
            axes[i, j].axis('off')

    plt.suptitle(
        f"VAE — Epoca {epoch} | {n_mass} Masse + {n_calc} Calcificazioni",
        fontsize=14, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    diagnose_lesion_quality(model, dataloader, DEVICE)
    calculate_vae_scaling_factor(model, train_loader, DEVICE)

    print("Keep up\n")

"""Training with possible resume"""

import torch, torch.nn.functional as F, os, gc
from torch.utils.data import DataLoader
from tqdm import tqdm

TRAIN_CFG = {
    'batch_size':       32,
    'epochs':           300,
    'lr':               1e-4,
    'gan_warmup':       278,
    'kl_warmup_steps':  800,
    'kl_target':        1e-6,
    'free_bits':        0.0,
    'w_l1':             0.50,
    'w_lpips':          0.60,
    'w_gdl':            4.00,
    'w_hf':             0.50,
    'w_adv':            0.30,
}

CKPT_STATE = os.path.join(MODELS_DIR, "training_state.pt")

train_loader = DataLoader(train_ds, batch_size=TRAIN_CFG['batch_size'],
                          shuffle=True,  num_workers=4, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=TRAIN_CFG['batch_size'],
                          shuffle=False, num_workers=2)

opt_vae  = torch.optim.AdamW(model.parameters(),      lr=TRAIN_CFG['lr'], weight_decay=1e-5)
opt_disc = torch.optim.AdamW(model_disc.parameters(), lr=TRAIN_CFG['lr'], weight_decay=1e-5)

scheduler_vae  = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    opt_vae,  T_0=50, T_mult=2, eta_min=1e-6)
scheduler_disc = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
    opt_disc, T_0=50, T_mult=2, eta_min=1e-6)

scaler = torch.amp.GradScaler('cuda')

global_step   = 0
best_val_loss = float('inf')
beg_epoch     = 0

if os.path.exists(CKPT_STATE):
    print(f"♻️ Resume da: {CKPT_STATE}")
    try:
        state = torch.load(CKPT_STATE, map_location=DEVICE)
        model.load_state_dict(state['model'])
        model_disc.load_state_dict(state['disc'])
        opt_vae.load_state_dict(state['opt_vae'])
        opt_disc.load_state_dict(state['opt_disc'])
        scheduler_vae.load_state_dict(state['sched_vae'])
        scheduler_disc.load_state_dict(state['sched_disc'])
        scaler.load_state_dict(state['scaler'])
        global_step   = state['global_step']
        best_val_loss = state['best_val_loss']
        beg_epoch     = state['epoch'] + 1
        print(f"✅ Ripreso da epoca {beg_epoch} | step={global_step} | best={best_val_loss:.5f}")
    except Exception as e:
        print(f"⚠️ Errore resume: {e} — parto da zero.")
else:
    print("🆕 Nessun checkpoint — training da zero.")

loss_fn_lpips.to(DEVICE)

def save_full_state(epoch, global_step, best_val_loss, tag="epoch"):
    torch.save({
        'epoch': epoch, 'global_step': global_step,
        'best_val_loss': best_val_loss,
        'model':      model.state_dict(),
        'disc':       model_disc.state_dict(),
        'opt_vae':    opt_vae.state_dict(),
        'opt_disc':   opt_disc.state_dict(),
        'sched_vae':  scheduler_vae.state_dict(),
        'sched_disc': scheduler_disc.state_dict(),
        'scaler':     scaler.state_dict(),
    }, CKPT_STATE)
    torch.save(model.state_dict(),      checkpoint_path)
    torch.save(model_disc.state_dict(), disc_checkpoint_path)
    print(f"💾 [{tag}] epoca {epoch} | step {global_step} | best {best_val_loss:.5f}")

print(f"🚀 Training VAE | {beg_epoch}→{TRAIN_CFG['epochs']} | "
      f"L1={TRAIN_CFG['w_l1']} LPIPS={TRAIN_CFG['w_lpips']} "
      f"GDL={TRAIN_CFG['w_gdl']} HF={TRAIN_CFG['w_hf']}")

for epoch in range(beg_epoch, TRAIN_CFG['epochs']):
    model.train()
    model_disc.train()
    pbar = tqdm(train_loader, desc=f"Epoca {epoch+1}/{TRAIN_CFG['epochs']}")

    for i, batch in enumerate(pbar):
        x          = batch["image"].to(DEVICE, non_blocking=True)
        d_loss_val = 0.0

        opt_vae.zero_grad(set_to_none=True)
        with torch.amp.autocast('cuda'):
            x_hat, mu, logvar = model(x)
            d_fake = model_disc(x_hat)
            v_loss, l1, lp, gdl, hf, adv, kl_w = vae_loss_engine(
                x, x_hat, mu, logvar, d_fake, global_step, TRAIN_CFG
            )

        scaler.scale(v_loss).backward()
        scaler.unscale_(opt_vae)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt_vae)

        if global_step > TRAIN_CFG['gan_warmup']:
            opt_disc.zero_grad(set_to_none=True)
            with torch.amp.autocast('cuda'):
                d_real     = model_disc(x)
                d_fake_det = model_disc(x_hat.detach())
                d_loss     = discriminator_loss(d_real, d_fake_det)
                d_loss_val = d_loss.item()
            scaler.scale(d_loss).backward()
            scaler.step(opt_disc)

        scaler.update()

        with torch.no_grad():
            cur_var = torch.exp(logvar.clamp(-6, 6)).mean().item()

        global_step += 1
        pbar.set_postfix({
            "L1":  f"{l1.item():.4f}",
            "LP":  f"{lp.item():.4f}",
            "GDL": f"{gdl.item():.4f}",
            "HF":  f"{hf.item():.4f}",
            "Var": f"{cur_var:.3f}",
            "D":   f"{d_loss_val:.4f}",
        })

    scheduler_vae.step()
    scheduler_disc.step()

    model.eval()
    val_l1 = 0.0
    with torch.no_grad():
        for b_v in val_loader:
            v_x       = b_v["image"].to(DEVICE)
            h_v, _, _ = model(v_x)
            val_l1   += F.l1_loss(h_v, v_x).item()

    avg_v  = val_l1 / len(val_loader)
    lr_now = opt_vae.param_groups[0]['lr']
    print(f"📊 Epoca {epoch+1} | Val L1: {avg_v:.5f} | Var: {cur_var:.3f} | LR: {lr_now:.2e}")

    save_full_state(epoch, global_step, best_val_loss, tag="epoch")

    if avg_v < best_val_loss:
        best_val_loss = avg_v
        torch.save(model.state_dict(), best_model_save_path)
        print(f"⭐ Nuovo best: {best_val_loss:.5f}")
        save_full_state(epoch, global_step, best_val_loss, tag="best")

    if (epoch + 1) % 5 == 0:
        visualize_reconstruction_v4(model, val_loader, DEVICE, epoch + 1)

gc.collect()
torch.cuda.empty_cache()
print(f"🏁 Training concluso | Best: {best_val_loss:.5f}")

"""### Sanity Checks


1.   Recostruction
2.   Laplacian Diff
3.   Generation

"""

import torch
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

@torch.no_grad()
def final_visual_inspection(model, dataloader, device, n_mass=5, n_calc=5):
    model.eval()

    mass_list = []
    calc_list = []

    for batch in dataloader:
        imgs = batch["image"]
        conds = batch["condition"]
        bboxes = batch["bbox"]

        for i in range(len(imgs)):
            is_mass = conds[i][0].item() == 1.0
            is_calc = conds[i][1].item() == 1.0

            if is_mass and len(mass_list) < n_mass:
                mass_list.append({"img": imgs[i], "bbox": bboxes[i], "type": "MASSA"})
            elif is_calc and len(calc_list) < n_calc:
                calc_list.append({"img": imgs[i], "bbox": bboxes[i], "type": "CALCIFICAZIONE"})

        if len(mass_list) >= n_mass and len(calc_list) >= n_calc:
            break

    all_samples = mass_list + calc_list
    n_total = len(all_samples)

    fig, axes = plt.subplots(n_total, 4, figsize=(20, 4 * n_total))

    col_names = ["Originale + BBox", "Ricostruzione VAE", "Residual (Error)", "Zoom Lesione (VAE)"]
    for ax, col in zip(axes[0], col_names):
        ax.set_title(col, fontsize=14, fontweight='bold', pad=15)

    for i, sample in enumerate(all_samples):
        x = sample["img"].unsqueeze(0).to(device)
        bbox = sample["bbox"]
        label = sample["type"]
        color = 'lime' if label == "MASSA" else 'yellow'

        x_hat, _, _ = model(x)

        orig = (x[0, 0].cpu() + 1.0) / 2.0
        recon = (x_hat[0, 0].cpu() + 1.0) / 2.0
        residual = torch.abs(orig - recon)

        axes[i, 0].imshow(orig, cmap='gray')
        if bbox.sum() > 0:
            rect = Rectangle((bbox[0], bbox[1]), bbox[2]-bbox[0], bbox[3]-bbox[1],
                             linewidth=2, edgecolor=color, facecolor='none')
            axes[i, 0].add_patch(rect)
        axes[i, 0].set_ylabel(label, fontsize=12, fontweight='bold', color=color)

        axes[i, 1].imshow(recon, cmap='gray')

        axes[i, 2].imshow(residual, cmap='magma')

        if bbox.sum() > 0:
            cx, cy = int((bbox[0]+bbox[2])/2), int((bbox[1]+bbox[3])/2)
            y1, y2 = max(0, cy-64), min(512, cy+64)
            x1, x2 = max(0, cx-64), min(512, cx+64)
            zoom_recon = recon[y1:y2, x1:x2]
            axes[i, 3].imshow(zoom_recon, cmap='gray')
            rx, ry = bbox[0]-x1, bbox[1]-y1
            rect_zoom = Rectangle((rx, ry), bbox[2]-bbox[0], bbox[3]-bbox[1],
                                  linewidth=1, edgecolor=color, facecolor='none')
            axes[i, 3].add_patch(rect_zoom)
        else:
            axes[i, 3].text(0.5, 0.5, "Senza BBox", ha='center')

        for j in range(4):
            axes[i, j].axis('off')

    plt.tight_layout()
    plt.show()

model.load_state_dict(torch.load(best_model_save_path, map_location=DEVICE))
print(f"✅ Analisi finale avviata sui pesi: {os.path.basename(best_model_save_path)}")

final_visual_inspection(model, test_loader, DEVICE)

"""

---

"""

def get_laplacian(x):
    kernel = torch.tensor([[[[0, 1, 0], [1, -4, 1], [0, 1, 0]]]], dtype=torch.float32).to(x.device)
    return F.conv2d(x, kernel, padding=1)

@torch.no_grad()
def sanity_check_laplacian(model, dataloader, device):
    model.eval()
    batch = next(iter(dataloader))
    x = batch["image"][:1].to(device)
    x_hat, _, _ = model(x)

    lap_orig = get_laplacian(x)
    lap_recon = get_laplacian(x_hat)
    lap_diff = torch.abs(lap_orig - lap_recon)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(lap_orig.cpu().squeeze(), cmap='magma')
    axes[0].set_title("Bordi Originali (Laplace)")

    axes[1].imshow(lap_recon.cpu().squeeze(), cmap='magma')
    axes[1].set_title("Bordi Ricostruiti")

    axes[2].imshow(lap_diff.cpu().squeeze(), cmap='hot')
    axes[2].set_title("Differenza Laplaciana (Artefatti)")

    for ax in axes: ax.axis('off')
    plt.show()

sanity_check_laplacian(model, val_loader, DEVICE)

"""

---

"""

@torch.no_grad()
def sanity_check_generation(model, device):
    model.eval()

    latent_ch = model.enc.mu.out_channels
    spatial_res = 64

    print(f"Sampling from latent space: [4, {latent_ch}, {spatial_res}, {spatial_res}]")

    z = torch.randn(4, latent_ch, spatial_res, spatial_res).to(device)

    samples = model.dec(z)

    samples = (samples + 1.0) / 2.0
    samples = samples.clamp(0, 1)

    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    for i in range(4):
        img_np = samples[i].cpu().squeeze().numpy()
        axes[i].imshow(img_np, cmap='gray')
        axes[i].set_title(f"Z-Sample {i+1}")
        axes[i].axis('off')

    plt.suptitle(f"Generazione VAE Zero-shot (8 Canali Latenti)", fontsize=16)
    plt.tight_layout()
    plt.show()

sanity_check_generation(model, DEVICE)

"""

---

"""

import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import shutil

@torch.no_grad()
def export_calcification_check(model, dataset, device, drive_folder="/content/drive/MyDrive/breast_blaster"):
    model.eval()

    temp_out_dir = "temp_calc_plots"
    zip_filename = "calc_check_visual"
    final_zip_path = os.path.join(drive_folder, zip_filename)

    os.makedirs(drive_folder, exist_ok=True)

    if os.path.exists(temp_out_dir):
        shutil.rmtree(temp_out_dir)
    os.makedirs(temp_out_dir, exist_ok=True)

    calc_df = dataset.meta_df[dataset.meta_df['Suspicious_Calcification'] == 1]
    calc_ids = calc_df.index.tolist()

    if not calc_ids:
        print("⚠️ Nessuna calcificazione trovata nel dataset.")
        return

    print(f"🔍 Trovate {len(calc_ids)} immagini con calcificazioni. Inizio esportazione su Drive...")

    for img_id in calc_ids:
        try:
            idx = dataset.ids.index(img_id)
        except ValueError:
            continue

        batch = dataset[idx]
        x = batch["image"].unsqueeze(0).to(device)
        bbox = batch["bbox"]
        row = dataset.meta_df.loc[img_id]
        view = row['view']

        x_hat, _, _ = model(x)

        orig_np = (x[0, 0].cpu().numpy() + 1.0) / 2.0
        recon_np = (x_hat[0, 0].cpu().numpy() + 1.0) / 2.0

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        axes[0].imshow(orig_np, cmap='gray')
        if bbox.sum() > 0:
            rect = Rectangle((bbox[0], bbox[1]), bbox[2]-bbox[0], bbox[3]-bbox[1],
                             linewidth=2, edgecolor='yellow', facecolor='none')
            axes[0].add_patch(rect)
        axes[0].set_title(f"ORIGINALE ({view})\nID: {img_id}")

        axes[1].imshow(recon_np, cmap='gray')
        axes[1].set_title("RICOSTRUZIONE VAE")

        if bbox.sum() > 0:
            cx, cy = int((bbox[0] + bbox[2]) / 2), int((bbox[1] + bbox[3]) / 2)
            y1, y2 = max(0, cy - 80), min(512, cy + 80)
            x1, x2 = max(0, cx - 80), min(512, cx + 80)
            axes[2].imshow(recon_np[y1:y2, x1:x2], cmap='gray')
            axes[2].set_title("ZOOM CALCIFICAZIONI")

        for ax in axes: ax.axis('off')

        plt.tight_layout()
        plt.savefig(os.path.join(temp_out_dir, f"calc_{view}_{img_id}.png"))
        plt.close()

    shutil.make_archive(final_zip_path, 'zip', temp_out_dir)

    shutil.rmtree(temp_out_dir)

    print(f"✅ Operazione completata!")
    print(f"📂 Lo ZIP è disponibile qui: {final_zip_path}.zip")

export_calcification_check(model, test_ds, DEVICE)

"""## Latent Data Preprocessing

Data upload
"""

import os
import shutil
import zipfile
import pandas as pd
from google.colab import drive

PROJECT_ROOT = "/content/drive/MyDrive/breast_blaster"
ZIP_SOURCE = os.path.join(PROJECT_ROOT, "init_dataset", "pre_latent.zip")
LOCAL_EXTRACT_PATH = "/content/breast_data"

if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

csv_path = None
if os.path.exists(LOCAL_EXTRACT_PATH):
    print(f"🔍 Ricerca CSV in {LOCAL_EXTRACT_PATH} esistente...")
    for root, dirs, files in os.walk(LOCAL_EXTRACT_PATH):
        if "latent.csv" in files:
            csv_path = os.path.join(root, "latent.csv")
            NEW_BASE_PATH = root
            break

if not csv_path:
    print(f"📦 Copia dello zip da {ZIP_SOURCE}...")
    if os.path.exists(LOCAL_EXTRACT_PATH):
        shutil.rmtree(LOCAL_EXTRACT_PATH)  # Cancella se corrotto

    shutil.copy(ZIP_SOURCE, "/content/pre_latent.zip")
    os.makedirs(LOCAL_EXTRACT_PATH, exist_ok=True)

    print("📦 Estrazione in corso...")
    with zipfile.ZipFile("/content/pre_latent.zip", 'r') as zip_ref:
        zip_ref.extractall(LOCAL_EXTRACT_PATH)
    print("✅ Estrazione completata.")

    # Cleanup
    try:
        os.remove("/content/pre_latent.zip")
    except:
        pass

print("\n🧹 Pulizia file spazzatura MacOS...")
for root, dirs, files in os.walk(LOCAL_EXTRACT_PATH):
    for d in list(dirs):
        if d in ["__MACOSX", ".ipynb_checkpoints"]:
            try:
                shutil.rmtree(os.path.join(root, d))
                dirs.remove(d)
            except:
                pass
    for f in files:
        if f in [".DS_Store", "desktop.ini"] or f.startswith("._"):
            try:
                os.remove(os.path.join(root, f))
            except:
                pass

print("\n🔍 Ricerca del file latent.csv...")
csv_path = None
NEW_BASE_PATH = None

for root, dirs, files in os.walk(LOCAL_EXTRACT_PATH):
    if "latent.csv" in files:
        csv_path = os.path.join(root, "latent.csv")
        NEW_BASE_PATH = root
        break

if csv_path:
    print(f"✅ CSV Trovato in: {csv_path}")
    df = pd.read_csv(csv_path)
    LOCAL_EXTRACT_PATH = NEW_BASE_PATH
    print(f"📊 Dataset caricato: {len(df)} righe.")
else:
    print("❌ latent.csv NON TROVATO. Contenuto della cartella:")
    import subprocess
    subprocess.run(f"find {LOCAL_EXTRACT_PATH} -maxdepth 3 -type f | head -20", shell=True)
    raise FileNotFoundError("Impossibile trovare latent.csv. Verifica il ZIP su Drive.")

contra_map = {}
for _, row in df.iterrows():
    key = (row['patient_id'], row['view'])
    if key not in contra_map:
        contra_map[key] = {}
    clean_id = str(row['image_id']).replace('.png', '')
    contra_map[key][row['laterality']] = clean_id

print(f"\n✅ Mappa Controlaterale costruita.")
print(f"📍 Base Path: {LOCAL_EXTRACT_PATH}")
print(f"📊 Pazienti unici: {df['patient_id'].nunique()}")

"""Latent data generation through trained VAE"""

import torch
import numpy as np
import os
from torch.utils.data import Dataset, DataLoader, ConcatDataset
from PIL import Image
from tqdm import tqdm

LATENT_OUT_DIR = "/content/latents_npy"
os.makedirs(LATENT_OUT_DIR, exist_ok=True)

class BreastDataset(Dataset):
    def __init__(self, split="train", df=None, contra_map=None, base_dir=None):
        self.split = split
        if os.path.exists(os.path.join(base_dir, "images", split)):
             self.base_path = os.path.join(base_dir, "images", split)
        else:
             self.base_path = os.path.join(base_dir, split)

        self.split_df = df[df['split'] == split].copy()
        self.split_df['image_id_clean'] = self.split_df['image_id'].astype(str).str.replace('.png', '', regex=False)
        self.ids = self.split_df['image_id_clean'].unique().tolist()
        self.meta_df = self.split_df.drop_duplicates('image_id_clean').set_index('image_id_clean')
        self.contra_map = contra_map
        self.images_cache = {}

        print(f"🧠 Caricamento {split.upper()} in RAM... ", end="")
        missing = 0
        for img_id in self.ids:
            potential_names = [f"{img_id}.png", img_id]
            found = False
            for name in potential_names:
                p = os.path.join(self.base_path, name)
                if os.path.exists(p):
                    with Image.open(p) as img:
                        self.images_cache[img_id] = np.array(img.convert('L'), dtype=np.float32) / 255.0
                    found = True
                    break
            if not found: missing += 1
        print(f"Fatto. (Mancanti: {missing})")

    def __len__(self): return len(self.ids)

    def __getitem__(self, idx):
        img_id = self.ids[idx]
        img_np = self.images_cache[img_id]
        img = torch.from_numpy(img_np).unsqueeze(0)
        img = (img * 2.0) - 1.0

        row = self.meta_df.loc[img_id]
        other_side = 'R' if row['laterality'] == 'L' else 'L'
        c_id = self.contra_map.get((row['patient_id'], row['view']), {}).get(other_side)
        c_id = str(c_id).replace('.png', '') if c_id else None

        if c_id and c_id in self.images_cache:
            c_img = torch.from_numpy(self.images_cache[c_id]).unsqueeze(0)
            c_img = (c_img * 2.0) - 1.0
        else:
            c_img = torch.flip(img, [2])

        return {"image": img, "contralateral": c_img, "img_id": img_id}

ds_train = BreastDataset("train", df, contra_map, base_dir=LOCAL_EXTRACT_PATH)
ds_val   = BreastDataset("val",   df, contra_map, base_dir=LOCAL_EXTRACT_PATH)
ds_test  = BreastDataset("test",  df, contra_map, base_dir=LOCAL_EXTRACT_PATH)

full_ds = ConcatDataset([ds_train, ds_val, ds_test])
full_loader = DataLoader(full_ds, batch_size=32, shuffle=False, num_workers=2)
train_calc_loader = DataLoader(ds_train, batch_size=32, shuffle=False)

@torch.no_grad()
def calculate_vae_scaling_factor(model, dataloader, device):
    model.eval()
    all_mus = []
    print("\n⏳ Analisi spazio latente per calcolo scaling factor...")
    for batch in tqdm(dataloader):
        x = batch["image"].to(device)
        mu, _ = model.enc(x)
        all_mus.append(mu.cpu())

    all_mus = torch.cat(all_mus, dim=0)
    latent_std = all_mus.std().item()
    latent_mean = all_mus.mean().item()
    scale_factor = 1.0 / latent_std

    print("\n" + "="*50)
    print(f"📊 ANALISI SPAZIO LATENTE")
    print(f"  > Media globale:     {latent_mean:.6f}")
    print(f"  > Dev. Std (sigma):  {latent_std:.6f}")
    print(f"  > Varianza (sigma²): {latent_std**2:.6f}")
    print("-" * 50)
    print(f"💎 SCALING FACTOR:    {scale_factor:.6f}")
    print("="*50)
    return scale_factor

VAE_SCALE = calculate_vae_scaling_factor(model, train_calc_loader, DEVICE)

print(f"\n🚀 Inizio estrazione definitiva latenti scalati (x {VAE_SCALE:.6f})...")
model.eval()
with torch.no_grad():
    for batch in tqdm(full_loader):
        imgs = batch["image"].to(DEVICE)
        ids = batch["img_id"]

        mu, _ = model.enc(imgs)
        latents = mu * VAE_SCALE

        latents_np = latents.cpu().numpy()
        for i, img_id in enumerate(ids):
            np.save(os.path.join(LATENT_OUT_DIR, f"{img_id}.npy"), latents_np[i])

print(f"\n✅ Operazione completata!")
print(f"📂 File .npy salvati: {len(os.listdir(LATENT_OUT_DIR))}")
print(f"📍 Directory: {LATENT_OUT_DIR}")

"""Visual sanity check"""

import matplotlib.pyplot as plt

@torch.no_grad()
def latent_sanity_check(df, latent_dir, model, device, scale_factor):
    model.eval()

    train_df = df[df['split'] == 'train']
    mass_samples = train_df[train_df['Mass'] == 1].sample(n=2, random_state=42)
    calc_samples = train_df[train_df['Suspicious_Calcification'] == 1].sample(n=5, random_state=42)

    samples = pd.concat([mass_samples, calc_samples])

    fig, axes = plt.subplots(len(samples), 4, figsize=(20, 4 * len(samples)))
    cols = ["Originale", "Ricostruzione (da Latente)", "Canale Latente 0", "Zoom Lesione"]
    for ax, col in zip(axes[0], cols): ax.set_title(col, fontsize=12, fontweight='bold')

    for i, (_, row) in enumerate(samples.iterrows()):
        img_id = str(row['image_id']).replace('.png', '')
        latent_path = os.path.join(latent_dir, f"{img_id}.npy")

        if not os.path.exists(latent_path):
            print(f"⚠️ Latente mancante: {img_id}")
            continue

        latent = np.load(latent_path)
        z = torch.from_numpy(latent).unsqueeze(0).to(device)

        z_unscaled = z / scale_factor
        rec = model.dec(z_unscaled)


        split = row['split']
        base_img_path = os.path.join(LOCAL_EXTRACT_PATH, "images", split)
        if not os.path.exists(base_img_path): base_img_path = os.path.join(LOCAL_EXTRACT_PATH, split)

        orig_path = os.path.join(base_img_path, f"{img_id}.png")
        if not os.path.exists(orig_path): orig_path = os.path.join(base_img_path, img_id)

        with Image.open(orig_path) as img_f:
            orig = np.array(img_f.convert('L')) / 255.0

        rec_vis = (rec[0, 0].cpu().numpy() + 1.0) / 2.0

        axes[i, 0].imshow(orig, cmap='gray')
        axes[i, 0].set_ylabel(f"{row['finding_categories']}\n{img_id}", fontsize=8)
        axes[i, 1].imshow(rec_vis, cmap='gray')
        axes[i, 2].imshow(latent[0], cmap='viridis')

        bbox = [row.get('new_xmin',0), row.get('new_ymin',0),
                row.get('new_xmax',512), row.get('new_ymax',512)]
        if bbox[2] > 0:
            cx, cy = int((bbox[0]+bbox[2])/2), int((bbox[1]+bbox[3])/2)
            y1, y2 = max(0, cy-64), min(512, cy+64)
            x1, x2 = max(0, cx-64), min(512, cx+64)
            axes[i, 3].imshow(rec_vis[y1:y2, x1:x2], cmap='gray')
            rect = plt.Rectangle((bbox[0]-x1, bbox[1]-y1), bbox[2]-bbox[0], bbox[3]-bbox[1],
                                 linewidth=1, edgecolor='red', facecolor='none')
            axes[i, 3].add_patch(rect)
        else:
            axes[i, 3].text(0.5, 0.5, "No BBox", ha='center')

    plt.tight_layout()
    plt.show()

latent_sanity_check(df, LATENT_OUT_DIR, model, DEVICE, VAE_SCALE)

"""Latent Dataset and Dataloader initialization"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import pandas as pd
from tqdm import tqdm

class LatentDataset(Dataset):
    def __init__(self, split="train", df=None, latent_dir="/content/latents_npy", contra_map=None):
        self.split = split
        self.split_df = df[df['split'] == split].copy()

        self.split_df['image_id_clean'] = self.split_df['image_id'].astype(str).str.replace('.png', '', regex=False)

        self.latent_dir = latent_dir
        self.contra_map = contra_map

        self.latents_cache = []
        self.contras_cache = []
        self.conditions = []
        self.bboxes = []
        self.captions = []
        self.ids = []

        print(f"🧠 Caricamento Latent Dataset ({split.upper()}) in RAM...")

        for _, row in tqdm(self.split_df.iterrows(), total=len(self.split_df)):
            img_id = row['image_id_clean']
            latent_path = os.path.join(self.latent_dir, f"{img_id}.npy")

            if not os.path.exists(latent_path):
                continue

            latent = np.load(latent_path)

            other_side = 'R' if row['laterality'] == 'L' else 'L'
            contra_id = self.contra_map.get((row['patient_id'], row['view']), {}).get(other_side)
            contra_id = str(contra_id).replace('.png', '') if contra_id else None

            contra_path = os.path.join(self.latent_dir, f"{contra_id}.npy") if contra_id else None

            if contra_path and os.path.exists(contra_path):
                contra_latent = np.load(contra_path)
            else:
                contra_latent = np.flip(latent, axis=2).copy()

            cond = [
                float(row['Mass']),
                float(row['Suspicious_Calcification']),
                float(row['density']) / 3.0
            ]

            bbox = [
                float(row.get('new_xmin', 0.0)),
                float(row.get('new_ymin', 0.0)),
                float(row.get('new_xmax', 0.0)),
                float(row.get('new_ymax', 0.0))
            ]

            caption = str(row.get('clip_annotation', "mammogram"))

            self.latents_cache.append(latent)
            self.contras_cache.append(contra_latent)
            self.conditions.append(cond)
            self.bboxes.append(bbox)
            self.captions.append(caption)
            self.ids.append(img_id)

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, idx):
        latent = torch.from_numpy(self.latents_cache[idx]).float()
        contra = torch.from_numpy(self.contras_cache[idx]).float()
        cond   = torch.tensor(self.conditions[idx], dtype=torch.float32)
        bbox   = torch.tensor(self.bboxes[idx], dtype=torch.float32)

        caption = self.captions[idx]
        img_id  = self.ids[idx]

        return {
            "image": latent,
            "contralateral": contra,
            "condition": cond,
            "bbox": bbox,
            "caption": caption,
            "img_id": img_id
        }

print("\n🚀 Inizializzazione Latent Dataloaders (Batch 64)...")

train_latent_ds = LatentDataset("train", df=df, latent_dir=LATENT_OUT_DIR, contra_map=contra_map)
val_latent_ds   = LatentDataset("val",   df=df, latent_dir=LATENT_OUT_DIR, contra_map=contra_map)
test_latent_ds  = LatentDataset("test",  df=df, latent_dir=LATENT_OUT_DIR, contra_map=contra_map)

train_loader = DataLoader(
    train_latent_ds,
    batch_size=64,
    shuffle=True,
    num_workers=2,
    pin_memory=True,
    drop_last=True
)

val_loader = DataLoader(
    val_latent_ds,
    batch_size=64,
    shuffle=False,
    num_workers=2,
    pin_memory=True
)

test_loader = DataLoader(
    test_latent_ds,
    batch_size=64,
    shuffle=False,
    num_workers=2
)

print(f"\n✅ Verifica Dimensioni Batch:")
try:
    sample = next(iter(train_loader))
    print(f" - Latent shape: {sample['image'].shape} (Deve essere [64, 4, 64, 64])")
    print(f" - Contra shape: {sample['contralateral'].shape}")
    print(f" - Condition shape: {sample['condition'].shape}")
    print(f" - Caption Example: \"{sample['caption'][0]}\"")
    print(f" - ID Example: {sample['img_id'][0]}")
except StopIteration:
    print("⚠️ Il dataset sembra vuoto. Controlla i path.")

"""## Denoiser stable-diffusion-2-inpainting

Setup
"""

from huggingface_hub import login
login()

import torch
import gc
from diffusers import StableDiffusionInpaintPipeline

model_id = "runwayml/stable-diffusion-inpainting"
print(f"🚀 Caricamento Pipeline da {model_id}...")

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    safety_checker=None
).to("cuda")

unet          = pipe.unet
text_encoder  = pipe.text_encoder
tokenizer     = pipe.tokenizer
noise_scheduler = pipe.scheduler

del pipe
gc.collect()
torch.cuda.empty_cache()

print(f"✅ UNet estratta. Canali input: {unet.config.in_channels}")
print(f"   VRAM dopo caricamento: {torch.cuda.memory_allocated()/1e9:.2f} GB")

"""CFG and Visualizer"""

CFG_CONFIG = {
    "guidance_scale":   7.5,
    "null_probability": 0.1,
    "uncond_prompt":    ""
}

print(f"✅ CFG configurato | Guidance: {CFG_CONFIG['guidance_scale']} | Dropout: {CFG_CONFIG['null_probability']}")

def get_weighted_text_embeddings(tokenizer, text_encoder, prompt, uncond_prompt, guidance_scale):
    text_inputs = tokenizer(prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt").to(DEVICE)
    uncond_inputs = tokenizer(uncond_prompt, padding="max_length", max_length=tokenizer.model_max_length, truncation=True, return_tensors="pt").to(DEVICE)

    prompt_embeds = text_encoder(text_inputs.input_ids)[0]
    uncond_embeds = text_encoder(uncond_inputs.input_ids)[0]

    return torch.cat([uncond_embeds, prompt_embeds])

print(f"✅ CFG Configurato (Guidance: {CFG_CONFIG['guidance_scale']}, Dropout: {CFG_CONFIG['null_probability']})")

import matplotlib.pyplot as plt
import torch
from matplotlib.patches import Rectangle

@torch.no_grad()
def monitor_training_progress(batch, unet,
                               n_mass=3, n_calc=4, n_healthy=2,
                               num_inference_steps=20):
    unet.eval()
    model.eval()

    conditions = batch["condition"]
    mass_idx, calc_idx, healthy_idx = [], [], []

    for i in range(len(conditions)):
        has_mass = conditions[i][0].item() == 1.0
        has_calc = conditions[i][1].item() == 1.0
        if has_mass and len(mass_idx) < n_mass:
            mass_idx.append(i)
        elif has_calc and not has_mass and len(calc_idx) < n_calc:
            calc_idx.append(i)
        elif not has_mass and not has_calc and len(healthy_idx) < n_healthy:
            healthy_idx.append(i)

    if len(calc_idx) < n_calc:
        for i in range(len(conditions)):
            if conditions[i][1].item() == 1.0 and i not in calc_idx and len(calc_idx) < n_calc:
                calc_idx.append(i)

    indices = mass_idx + calc_idx + healthy_idx
    labels  = (["MASSA"] * len(mass_idx) +
               ["CALCIFICAZIONE"] * len(calc_idx) +
               ["SANO"] * len(healthy_idx))
    colors  = {"MASSA": "lime", "CALCIFICAZIONE": "yellow", "SANO": "cyan"}

    if not indices:
        print("⚠️ Nessun campione trovato.")
        unet.train(); model.train()
        return

    latents  = batch["image"].to(DEVICE, dtype=torch.float32)
    bboxes   = batch["bbox"].cpu()
    captions = batch["caption"]

    fig, axes = plt.subplots(len(indices), 4, figsize=(24, 5 * len(indices)))
    if len(indices) == 1:
        axes = axes.reshape(1, -1)

    col_titles = ["Input Mascherato", "Ground Truth", "Generazione", "Prompt & Info"]
    for j, t in enumerate(col_titles):
        axes[0, j].set_title(t, fontsize=12, fontweight='bold')

    print(f"🎨 Generando {len(indices)} campioni "
          f"({len(mass_idx)}M / {len(calc_idx)}C / {len(healthy_idx)}S)...")

    for i, (idx, label) in enumerate(zip(indices, labels)):
        color = colors[label]
        bbox  = bboxes[idx]

        mask = torch.zeros((1, 1, 64, 64), device=DEVICE, dtype=torch.float32)
        if bbox.sum() > 0:
            x0 = max(int(bbox[0].item() / 8), 0)
            y0 = max(int(bbox[1].item() / 8), 0)
            x1 = min(int(bbox[2].item() / 8), 64)
            y1 = min(int(bbox[3].item() / 8), 64)
            if x1 > x0 and y1 > y0:
                mask[0, 0, y0:y1, x0:x1] = 1.0

        original_latent = latents[idx:idx+1]
        masked_latent   = original_latent * (1.0 - mask)

        inputs = tokenizer(
            [captions[idx]], padding="max_length",
            max_length=tokenizer.model_max_length,
            truncation=True, return_tensors="pt"
        ).to(DEVICE)
        with torch.amp.autocast('cuda'):
            enc_hs = text_encoder(inputs.input_ids)[0]

        noise_scheduler.set_timesteps(num_inference_steps)
        latents_gen = torch.randn((1, 4, 64, 64), device=DEVICE, dtype=torch.float32)
        for t in noise_scheduler.timesteps:
            model_input = torch.cat([latents_gen, mask, masked_latent], dim=1)
            with torch.amp.autocast('cuda'):
                noise_pred = unet(model_input, t, enc_hs).sample
            latents_gen = noise_scheduler.step(
                noise_pred.float(), t, latents_gen
            ).prev_sample

        with torch.amp.autocast('cuda'):
            gt_dec  = model.dec(original_latent / VA_SCALE).detach().float()
            gen_dec = model.dec(latents_gen     / VA_SCALE).detach().float()

        gt_np  = ((gt_dec[0, 0].cpu().numpy()  + 1.0) / 2.0).clip(0, 1)
        gen_np = ((gen_dec[0, 0].cpu().numpy() + 1.0) / 2.0).clip(0, 1)

        def add_bbox(ax, img_np, linestyle="-"):
            if bbox.sum() > 0:
                s  = img_np.shape[0] / 512.0
                x0b = float(bbox[0]) * s
                y0b = float(bbox[1]) * s
                w   = (float(bbox[2]) - float(bbox[0])) * s
                h   = (float(bbox[3]) - float(bbox[1])) * s
                ax.add_patch(Rectangle(
                    (x0b, y0b), w, h,
                    linewidth=2, edgecolor=color,
                    facecolor='none', linestyle=linestyle
                ))

        vis = masked_latent[0, 0].cpu().float().numpy()
        vis = (vis - vis.min()) / (vis.max() - vis.min() + 1e-8)
        axes[i, 0].imshow(vis, cmap='magma')
        axes[i, 0].set_ylabel(label, fontsize=11, fontweight='bold', color=color)
        axes[i, 0].axis('off')

        axes[i, 1].imshow(gt_np, cmap='gray')
        add_bbox(axes[i, 1], gt_np, linestyle="--")
        axes[i, 1].axis('off')

        axes[i, 2].imshow(gen_np, cmap='gray')
        add_bbox(axes[i, 2], gen_np, linestyle="-")
        axes[i, 2].axis('off')

        axes[i, 3].text(
            0.05, 0.5,
            f"CLASSE: {label}\n\nPROMPT:\n{captions[idx]}",
            fontsize=9, verticalalignment='center',
            color='white', backgroundcolor='black',
            wrap=True, transform=axes[i, 3].transAxes
        )
        axes[i, 3].set_facecolor('black')
        axes[i, 3].axis('off')

    plt.suptitle(
        f"Monitor Training | {len(mass_idx)} Masse | {len(calc_idx)} Calc | {len(healthy_idx)} Sani",
        fontsize=14, fontweight='bold'
    )
    plt.tight_layout()
    plt.show()

    unet.train(); model.train()
    print("🔄 Train() ripristinato.")

"""LoRa Configuration"""

from peft import LoraConfig, get_peft_model

CHECKPOINT_DIR       = os.path.join(PROJECT_ROOT, "checkpoints_lora")
resume_checkpoint_path = os.path.join(CHECKPOINT_DIR, "best_lora_model")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

lora_config = LoraConfig(
    r=16,
    lora_alpha=16,
    target_modules=["to_q", "to_k", "to_v", "to_out.0"],
    lora_dropout=0.05,
    bias="none",
)

unet = get_peft_model(unet, lora_config)
print("✅ LoRA iniettato.")

for name, param in unet.named_parameters():
    if not param.requires_grad:
        param.data = param.data.half()
for name, param in unet.named_parameters():
    if param.requires_grad:
        param.data = param.data.float()

text_encoder.requires_grad_(False)
unet.train()

lora_dtypes   = {p.dtype for p in unet.parameters() if p.requires_grad}
frozen_dtypes = {p.dtype for p in unet.parameters() if not p.requires_grad}
assert lora_dtypes   == {torch.float32}, f"❌ LoRA non è FP32: {lora_dtypes}"
assert frozen_dtypes == {torch.float16}, f"❌ Frozen non è FP16: {frozen_dtypes}"

unet.print_trainable_parameters()
print(f"   LoRA dtype   : {lora_dtypes}")
print(f"   Frozen dtype : {frozen_dtypes}")
print(f"   VRAM attuale : {torch.cuda.memory_allocated()/1e9:.2f} GB")

"""Training"""

import torch, torch.nn.functional as F
import os, gc
import safetensors.torch
from peft import set_peft_model_state_dict
from tqdm import tqdm

NUM_EPOCHS      = 200
SAVE_EVERY      = 5
VISUALIZE_EVERY = 5
LR              = 2e-4

CHECKPOINT_DIR        = os.path.join(PROJECT_ROOT, "checkpoints_lora")
resume_checkpoint_path = os.path.join(CHECKPOINT_DIR, "best_lora_model")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

optimizer = torch.optim.AdamW(
    [p for p in unet.parameters() if p.requires_grad],
    lr=LR, weight_decay=1e-2
)
scaler = torch.amp.GradScaler('cuda')

LAST_EPOCH  = 0
GLOBAL_STEP = 0
best_loss   = float('inf')

adapter_safe = os.path.join(resume_checkpoint_path, "adapter_model.safetensors")
adapter_bin  = os.path.join(resume_checkpoint_path, "adapter_model.bin")
meta_path    = os.path.join(resume_checkpoint_path, "training_state.pt")

if os.path.exists(adapter_safe) or os.path.exists(adapter_bin):
    print(f"♻️ Checkpoint trovato: {resume_checkpoint_path}")
    try:
        if os.path.exists(adapter_safe):
            sd = safetensors.torch.load_file(adapter_safe, device=DEVICE)
        else:
            sd = torch.load(adapter_bin, map_location=DEVICE)
        set_peft_model_state_dict(unet, sd)

        for param in unet.parameters():
            if param.requires_grad:
                param.data = param.data.float()
        print("✅ Pesi LoRA caricati e in FP32.")

        if os.path.exists(meta_path):
            state = torch.load(meta_path, map_location="cpu")
            LAST_EPOCH  = state["epoch"] + 1
            GLOBAL_STEP = state["global_step"]
            best_loss   = state["best_loss"]
            optimizer.load_state_dict(state["optimizer"])
            scaler.load_state_dict(state["scaler"])
            print(f"✅ Stato ripristinato | Epoca: {LAST_EPOCH} | "
                  f"Step: {GLOBAL_STEP} | Best: {best_loss:.6f}")
        else:
            print("ℹ️ Nessun training_state.pt — optimizer riparte da zero.")

    except Exception as e:
        print(f"⚠️ Errore caricamento: {e} — training da zero.")
else:
    print("🆕 Nessun checkpoint — training da zero.")

lora_dt   = {p.dtype for p in unet.parameters() if p.requires_grad}
frozen_dt = {p.dtype for p in unet.parameters() if not p.requires_grad}
assert lora_dt   == {torch.float32}, f"❌ LoRA dtype errato: {lora_dt}"
assert frozen_dt == {torch.float16}, f"❌ Frozen dtype errato: {frozen_dt}"
print(f"   LoRA: {lora_dt} | Frozen: {frozen_dt} | "
      f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")


def save_checkpoint(epoch, global_step, avg_loss, tag="periodic"):
    save_dir = (os.path.join(CHECKPOINT_DIR, "best_lora_model")
                if tag == "best"
                else os.path.join(CHECKPOINT_DIR, f"lora_epoch_{epoch+1}"))
    os.makedirs(save_dir, exist_ok=True)

    unet.save_pretrained(save_dir)

    torch.save({
        "epoch":       epoch,
        "global_step": global_step,
        "best_loss":   best_loss,
        "optimizer":   optimizer.state_dict(),
        "scaler":      scaler.state_dict(),
    }, os.path.join(save_dir, "training_state.pt"))

    print(f"💾 [{tag}] epoca {epoch+1} | step {global_step} | loss {avg_loss:.6f} → {save_dir}")

def train_inpainting_lora():
    global best_loss, GLOBAL_STEP

    unet.train()
    model.eval()

    print(f"\n🚀 LoRA Training | Epoche: {LAST_EPOCH}→{NUM_EPOCHS} | "
          f"LR: {LR} | Best: {best_loss:.6f} | Step: {GLOBAL_STEP}")

    for epoch in range(LAST_EPOCH, NUM_EPOCHS):
        pbar       = tqdm(train_loader, desc=f"Epoca {epoch+1}/{NUM_EPOCHS}")
        epoch_loss = 0.0

        for step, batch in enumerate(pbar):
            latents  = batch["image"].to(DEVICE, dtype=torch.float16)
            bboxes   = batch["bbox"].to(DEVICE)
            captions = batch["caption"]

            mask = torch.zeros(
                (latents.shape[0], 1, 64, 64),
                device=DEVICE, dtype=torch.float16
            )
            for i, bbox in enumerate(bboxes):
                if bbox.sum() > 0:
                    x0 = max(int(bbox[0].item() / 8), 0)
                    y0 = max(int(bbox[1].item() / 8), 0)
                    x1 = min(int(bbox[2].item() / 8), 64)
                    y1 = min(int(bbox[3].item() / 8), 64)
                    if y1 > y0 and x1 > x0:
                        mask[i, 0, y0:y1, x0:x1] = 1.0

            masked_latents = latents * (1.0 - mask)

            processed_captions = [
                "" if torch.rand(1).item() < CFG_CONFIG["null_probability"] else cap
                for cap in captions
            ]
            inputs = tokenizer(
                processed_captions, padding="max_length",
                max_length=tokenizer.model_max_length,
                truncation=True, return_tensors="pt"
            ).to(DEVICE)

            with torch.no_grad():
                enc_hs = text_encoder(inputs.input_ids)[0]

            noise     = torch.randn_like(latents)
            timesteps = torch.randint(
                0, noise_scheduler.config.num_train_timesteps,
                (latents.shape[0],), device=DEVICE
            ).long()
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            model_input = torch.cat([noisy_latents, mask, masked_latents], dim=1)

            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast('cuda'):
                noise_pred = unet(model_input, timesteps, enc_hs).sample
                loss = F.mse_loss(noise_pred.float(), noise.float())

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(
                [p for p in unet.parameters() if p.requires_grad], 1.0
            )
            scaler.step(optimizer)
            scaler.update()

            epoch_loss  += loss.item()
            GLOBAL_STEP += 1
            pbar.set_postfix(
                loss=f"{loss.item():.5f}",
                vram=f"{torch.cuda.memory_allocated()/1e9:.1f}GB"
            )

        avg_loss = epoch_loss / len(train_loader)
        print(f"📊 Epoca {epoch+1}/{NUM_EPOCHS} | "
              f"Loss: {avg_loss:.6f} | Step: {GLOBAL_STEP} | "
              f"VRAM: {torch.cuda.memory_allocated()/1e9:.1f} GB")

        if (epoch + 1) % VISUALIZE_EVERY == 0:
            monitor_training_progress(batch, unet)

        if (epoch + 1) % SAVE_EVERY == 0:
            save_checkpoint(epoch, GLOBAL_STEP, avg_loss, tag="periodic")

        if avg_loss < best_loss:
            best_loss = avg_loss
            save_checkpoint(epoch, GLOBAL_STEP, avg_loss, tag="best")
            print(f"⭐ Nuovo best: {best_loss:.6f}")

    print(f"\n🏁 Training concluso | Best: {best_loss:.6f} | Step: {GLOBAL_STEP}")


train_inpainting_lora()

"""## Results: testing, experimental inference and baseline

### Metrics: FID and SSIM
"""

import torch
import numpy as np
from skimage.metrics import structural_similarity as ssim
from torch.nn.functional import interpolate
import torchvision.models as models
from torchvision.models import Inception_V3_Weights

# SSIM: Structural Similarity Index

def compute_ssim_batch(img_real: np.ndarray, img_gen: np.ndarray,
                        data_range: int = 255) -> tuple:

    if img_real.ndim == 4 and img_real.shape[1] == 1:
        img_real = img_real.squeeze(1)
    if img_gen.ndim == 4 and img_gen.shape[1] == 1:
        img_gen = img_gen.squeeze(1)

    assert img_real.shape == img_gen.shape, \
        f"Shape mismatch: {img_real.shape} vs {img_gen.shape}"

    ssim_scores = []
    for i in range(img_real.shape[0]):
        score = ssim(img_real[i].astype(np.float32),
                     img_gen[i].astype(np.float32),
                     data_range=data_range)
        ssim_scores.append(score)

    return np.mean(ssim_scores), np.std(ssim_scores)

# FID: Fréchet Inception Distance con pesi ImageNet

class FIDCalculator:

    def __init__(self, device='cuda'):
        self.device = device

        self.inception = models.inception_v3(
            weights=Inception_V3_Weights.DEFAULT,
            aux_logits=True,
            transform_input=True
        )

        self.inception = torch.nn.Sequential(
            self.inception.Conv2d_1a_3x3,
            self.inception.Conv2d_2a_3x3,
            self.inception.Conv2d_2b_3x3,
            torch.nn.MaxPool2d(kernel_size=3, stride=2),
            self.inception.Conv2d_3b_1x1,
            self.inception.Conv2d_4a_3x3,
            torch.nn.MaxPool2d(kernel_size=3, stride=2),
            self.inception.Mixed_5b,
            self.inception.Mixed_5c,
            self.inception.Mixed_5d,
            self.inception.Mixed_6a,
            self.inception.Mixed_6b,
            self.inception.Mixed_6c,
            self.inception.Mixed_6d,
            self.inception.Mixed_6e,
            self.inception.Mixed_7a,
            self.inception.Mixed_7b,
            self.inception.Mixed_7c,
            torch.nn.AdaptiveAvgPool2d((1, 1))
        )

        self.inception = self.inception.to(device)
        self.inception.eval()
        for p in self.inception.parameters():
            p.requires_grad = False

        print("✅ InceptionV3 caricato con pesi ImageNet DEFAULT")

    def extract_features(self, img_batch: np.ndarray) -> np.ndarray:
        if img_batch.ndim == 3:
            img_batch = np.stack([img_batch]*3, axis=1)

        img_tensor = torch.from_numpy(img_batch.astype(np.float32)).to(self.device)
        img_tensor = img_tensor / 255.0

        img_tensor = interpolate(img_tensor, size=(299, 299),
                                  mode='bilinear', align_corners=False)

        with torch.no_grad():
            features = self.inception(img_tensor)
            features = features.flatten(start_dim=1)

        return features.cpu().numpy()

    def compute_fid(self, real_features: np.ndarray,
                    gen_features: np.ndarray) -> float:

        mu_real = np.mean(real_features, axis=0)
        mu_gen  = np.mean(gen_features, axis=0)

        sigma_real = np.cov(real_features.T)
        sigma_gen  = np.cov(gen_features.T)

        diff_mean = np.sum((mu_real - mu_gen) ** 2)

        try:
            eigvals_r, eigvecs_r = np.linalg.eigh(sigma_real + 1e-6*np.eye(2048))
            eigvals_g, eigvecs_g = np.linalg.eigh(sigma_gen + 1e-6*np.eye(2048))

            sqrt_r = eigvecs_r @ np.diag(np.sqrt(np.clip(eigvals_r, 0, None))) @ eigvecs_r.T

            prod = sqrt_r @ sigma_gen @ sqrt_r
            eigvals_p, eigvecs_p = np.linalg.eigh(prod + 1e-6*np.eye(2048))
            sqrt_prod = eigvecs_p @ np.diag(np.sqrt(np.clip(eigvals_p, 0, None))) @ eigvecs_p.T

            trace_term = np.trace(sigma_real + sigma_gen - 2*sqrt_prod)
        except Exception as e:
            print(f"⚠️ Stabilità numerica: {e}")
            trace_term = np.trace(sigma_real + sigma_gen)

        fid = diff_mean + trace_term
        return float(np.clip(fid, 0, 1e6))

print("✅ Metriche setup completato (SSIM + FID con ImageNet weights)")

"""### Testing

setup
"""

from huggingface_hub import login
login()

import gc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw
from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
import safetensors.torch

MODEL_ID            = "runwayml/stable-diffusion-inpainting"
NUM_INFERENCE_STEPS = 50
GUIDANCE_SCALE      = 7.5
CHECKPOINT_DIR        = os.path.join(PROJECT_ROOT, "checkpoints_lora")
resume_checkpoint_path = os.path.join(CHECKPOINT_DIR, "best_lora_model")
VAE_SCALE = calculate_vae_scaling_factor(model, train_calc_loader, DEVICE)
print(f"✅ VAE_SCALE: {VAE_SCALE}")

print(f"\n🚀 Caricamento SD Pipeline ({MODEL_ID})...")
pipe = StableDiffusionInpaintPipeline.from_pretrained(
    MODEL_ID, torch_dtype=torch.float16, safety_checker=None
).to(DEVICE)

unet            = pipe.unet
text_encoder    = pipe.text_encoder
tokenizer       = pipe.tokenizer
noise_scheduler = pipe.scheduler

del pipe; gc.collect(); torch.cuda.empty_cache()
print(f"✅ SD estratta. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

lora_config = LoraConfig(
    r=16, lora_alpha=16,
    target_modules=["to_q", "to_k", "to_v", "to_out.0"],
    lora_dropout=0.05, bias="none",
)
unet = get_peft_model(unet, lora_config)

lora_dir     = os.path.join(CHECKPOINT_DIR, "best_lora_model")
adapter_safe = os.path.join(lora_dir, "adapter_model.safetensors")
adapter_bin  = os.path.join(lora_dir, "adapter_model.bin")

if os.path.exists(adapter_safe):
    sd = safetensors.torch.load_file(adapter_safe, device=DEVICE)
elif os.path.exists(adapter_bin):
    sd = torch.load(adapter_bin, map_location=DEVICE)
else:
    raise FileNotFoundError(f"❌ Nessun checkpoint LoRA in {lora_dir}")

set_peft_model_state_dict(unet, sd)

for p in unet.parameters():
    p.data = p.data.float() if p.requires_grad else p.data.half()
text_encoder.requires_grad_(False)
unet.eval(); text_encoder.eval(); model.eval()

lora_dt   = {p.dtype for p in unet.parameters() if p.requires_grad}
frozen_dt = {p.dtype for p in unet.parameters() if not p.requires_grad}
assert lora_dt   == {torch.float32}, f"❌ LoRA dtype: {lora_dt}"
assert frozen_dt == {torch.float16}, f"❌ Frozen dtype: {frozen_dt}"
print(f"✅ LoRA caricato | LoRA={lora_dt} | Frozen={frozen_dt}")
print(f"   VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

DDIM_SCHEDULER = DDIMScheduler.from_config(noise_scheduler.config)
DDIM_SCHEDULER.set_timesteps(NUM_INFERENCE_STEPS)
print("✅ DDIM configurato.")

def decode_scaled_latent(latent_scaled: torch.Tensor) -> np.ndarray:
    with torch.no_grad():
        lat = (latent_scaled.float() / VAE_SCALE).to(DEVICE)
        if lat.dim() == 3: lat = lat.unsqueeze(0)
        imgs = model.dec(lat)
    return ((imgs.cpu().float().squeeze(1).numpy() + 1) / 2 * 255)\
           .clip(0, 255).astype(np.uint8)


def bbox_to_latent_mask(bbox: torch.Tensor) -> torch.Tensor:
    mask = torch.zeros(1, 1, 64, 64, dtype=torch.float16, device=DEVICE)
    if bbox.sum() > 0:
        x0 = max(int(bbox[0].item() / 8), 0)
        y0 = max(int(bbox[1].item() / 8), 0)
        x1 = min(int(bbox[2].item() / 8), 64)
        y1 = min(int(bbox[3].item() / 8), 64)
        if y1 > y0 and x1 > x0:
            mask[0, 0, y0:y1, x0:x1] = 1.0
    return mask


@torch.no_grad()
def inpaint_latent(
    base_latent: torch.Tensor,
    mask: torch.Tensor,
    caption: str,
    unet_model=None,
    num_steps: int = NUM_INFERENCE_STEPS,
    guidance_scale: float = GUIDANCE_SCALE,
    init_noise: torch.Tensor = None,
) -> torch.Tensor:

    if unet_model is None:
        unet_model = unet
    scheduler = DDIMScheduler.from_config(noise_scheduler.config)
    scheduler.set_timesteps(num_steps)

    base_latent = base_latent.to(DEVICE, dtype=torch.float16)
    mask        = mask.to(DEVICE, dtype=torch.float16)
    masked_lat  = base_latent * (1 - mask)

    tok_out  = tokenizer(
        [caption, ""], padding="max_length",
        max_length=tokenizer.model_max_length,
        truncation=True, return_tensors="pt"
    ).to(DEVICE)
    text_emb = text_encoder(tok_out.input_ids)[0]

    noisy = init_noise.to(DEVICE, dtype=torch.float16) if init_noise is not None \
            else torch.randn_like(base_latent)

    for t in scheduler.timesteps:
        noisy_d = torch.cat([noisy]*2)
        mask_d  = torch.cat([mask]*2)
        mld     = torch.cat([masked_lat]*2)
        mi      = torch.cat([noisy_d, mask_d, mld], dim=1)
        with torch.amp.autocast('cuda'):
            np_ = unet_model(mi, t, text_emb).sample
        np_text, np_uncond = np_[0:1], np_[1:2]
        noise_pred = np_uncond + guidance_scale * (np_text - np_uncond)
        noisy = scheduler.step(noise_pred, t, noisy).prev_sample

    return noisy * mask + base_latent * (1 - mask)


def find_by_condition(dataset, cond_type: str, n: int,
                      view: str = None, lat: str = None) -> list:
    results = []
    for i, cond in enumerate(dataset.conditions):
        if view and dataset.views[i] != view: continue
        if lat  and dataset.lateralities[i] != lat: continue
        match = (
            (cond_type == 'mass'    and cond[0] == 1.0 and cond[1] == 0.0) or
            (cond_type == 'calc'    and cond[1] == 1.0 and cond[0] == 0.0) or
            (cond_type == 'healthy' and cond[0] == 0.0 and cond[1] == 0.0)
        )
        if match: results.append(i)
        if len(results) >= n: break
    return results

print(f"\n✅ Setup completato — pronto per inferenza.")
print(f"   Train: {len(train_latent_ds)} | Val: {len(val_latent_ds)} | Test: {len(test_latent_ds)}")

def patch_latent_dataset_metadata(ds, df):
    df_clean = df.copy()
    df_clean['image_id_clean'] = df_clean['image_id'].astype(str)\
                                   .str.replace('.png','',regex=False)
    meta = df_clean.drop_duplicates('image_id_clean')\
                   .set_index('image_id_clean')[['view','laterality']]

    ds.views        = []
    ds.lateralities = []
    for img_id in ds.ids:
        if img_id in meta.index:
            ds.views.append(meta.loc[img_id, 'view'])
            ds.lateralities.append(meta.loc[img_id, 'laterality'])
        else:
            ds.views.append('CC')
            ds.lateralities.append('R')

    print(f"✅ {ds.split.upper()}: views e lateralities aggiunti "
          f"({len(ds.views)} entries)")

patch_latent_dataset_metadata(train_latent_ds, df)
patch_latent_dataset_metadata(val_latent_ds,   df)
patch_latent_dataset_metadata(test_latent_ds,  df)

"""Testing"""

unet.eval(); model.eval()

mass_idx    = find_by_condition(test_latent_ds, 'mass',    4)
calc_idx    = find_by_condition(test_latent_ds, 'calc',    4)
healthy_idx = find_by_condition(test_latent_ds, 'healthy', 2)

if len(mass_idx)    < 4: mass_idx    += find_by_condition(val_latent_ds, 'mass',    4 - len(mass_idx))
if len(calc_idx)    < 4: calc_idx    += find_by_condition(val_latent_ds, 'calc',    4 - len(calc_idx))
if len(healthy_idx) < 2: healthy_idx += find_by_condition(val_latent_ds, 'healthy', 2 - len(healthy_idx))

samples = (
    [('Massa',   test_latent_ds, i) for i in mass_idx]    +
    [('Calc.',   test_latent_ds, i) for i in calc_idx]    +
    [('Sana',    test_latent_ds, i) for i in healthy_idx]
)

print(f"⏳ Inpainting {len(samples)} campioni...")
results = []

for label, ds, idx in tqdm(samples):
    latent_t   = torch.from_numpy(ds.latents_cache[idx]).unsqueeze(0).float()
    bbox       = torch.tensor(ds.bboxes[idx])
    caption    = ds.captions[idx]
    has_lesion = ds.conditions[idx][0] > 0 or ds.conditions[idx][1] > 0

    gt_img = decode_scaled_latent(latent_t)[0]

    if has_lesion and bbox.sum() > 0:
        mask         = bbox_to_latent_mask(bbox)
        inpainted    = inpaint_latent(latent_t, mask, caption)
        rec_img      = decode_scaled_latent(inpainted)[0]
    else:
        rec_img = gt_img.copy()

    diff_img = np.clip(
        np.abs(gt_img.astype(np.int16) - rec_img.astype(np.int16)) * 3,
        0, 255
    ).astype(np.uint8)

    results.append((label, ds.ids[idx], gt_img, rec_img, diff_img))

n = len(results)
fig, axes = plt.subplots(n, 3, figsize=(12, 4*n))
if n == 1: axes = axes[np.newaxis, :]
fig.suptitle("Testing — GT vs Ricostruzione LDM Inpainting", fontsize=14, y=1.01)

for c, title in enumerate(["GT (decoded latent)",
                            "Ricostruzione (Denoiser + VAE Dec.)",
                            "Differenza Assoluta ×3"]):
    axes[0, c].set_title(title, fontsize=10, fontweight='bold')

for r, (label, img_id, gt, rec, diff) in enumerate(results):
    axes[r, 0].imshow(gt,   cmap='gray', vmin=0, vmax=255)
    axes[r, 1].imshow(rec,  cmap='gray', vmin=0, vmax=255)
    axes[r, 2].imshow(diff, cmap='hot',  vmin=0, vmax=255)
    axes[r, 0].set_ylabel(f"{label}\n{img_id[:10]}…", fontsize=8,
                           rotation=0, labelpad=60, va='center')
    for c in range(3): axes[r, c].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "testing_reconstruction.png"), dpi=120, bbox_inches='tight')
plt.show()
print("✅ Salvato.")

"""Metrics"""

import numpy as np
import pandas as pd

print("=" * 70)
print("TESTING METRICS: SSIM + FID")
print("=" * 70)

gt_images  = np.array([r[2] for r in results])
rec_images = np.array([r[3] for r in results])

print(f"\n📊 Batch Testing: {len(results)} campioni")
print(f"   GT shape:  {gt_images.shape}")
print(f"   REC shape: {rec_images.shape}")

# SSIM
ssim_mean, ssim_std = compute_ssim_batch(gt_images, rec_images, data_range=255)

print(f"\n🔍 SSIM (Structural Similarity):")
print(f"   Mean: {ssim_mean:.4f}")
print(f"   Std:  {ssim_std:.4f}")

# FID
fid_calc = FIDCalculator(device=DEVICE)

print(f"\n⏳ Estrazione feature InceptionV3...")
features_gt  = fid_calc.extract_features(gt_images)
features_rec = fid_calc.extract_features(rec_images)

fid_score = fid_calc.compute_fid(features_gt, features_rec)

print(f"\n🎯 FID (Fréchet Inception Distance):")
print(f"   Score: {fid_score:.2f}")

# Summary Table
metrics_df = pd.DataFrame({
    'Metrica': ['SSIM', 'SSIM_std', 'FID'],
    'Valore': [f'{ssim_mean:.4f}', f'{ssim_std:.4f}', f'{fid_score:.2f}'],
    'Interpretazione': [
        '↑ Similarity pixel-space',
        'Variabilità SSIM',
        '↓ Distribuzione latente'
    ]
})

print("\n" + "=" * 70)
print(metrics_df.to_string(index=False))
print("=" * 70)

"""### Inference

Lesions Transfer
"""

unet.eval(); model.eval()

h_idx = find_by_condition(test_latent_ds, 'healthy', 1)[0]
h_lat = torch.from_numpy(test_latent_ds.latents_cache[h_idx]).float()
h_view, h_side = test_latent_ds.views[h_idx], test_latent_ds.lateralities[h_idx]
h_id   = test_latent_ds.ids[h_idx]
healthy_img = decode_scaled_latent(h_lat.unsqueeze(0))[0]
print(f"🩻 Sana: {h_id[:16]}…  view={h_view}  lat={h_side}")

def get_lesion_idx(ds, ctype, n, view, lat):
    idx = find_by_condition(ds, ctype, n, view=view, lat=lat)
    if len(idx) < n: idx = find_by_condition(ds, ctype, n, view=view)
    if len(idx) < n: idx = find_by_condition(ds, ctype, n)
    return idx[:n]

mass_idx_t = get_lesion_idx(test_latent_ds, 'mass', 3, h_view, h_side)
calc_idx_t = get_lesion_idx(test_latent_ds, 'calc', 3, h_view, h_side)
lesions = [('Massa', i) for i in mass_idx_t] + [('Calc.', i) for i in calc_idx_t]
print(f"  Masse: {[test_latent_ds.ids[i][:8] for _,i in lesions[:3]]}")
print(f"  Calc.: {[test_latent_ds.ids[i][:8] for _,i in lesions[3:]]}")

print("\n⏳ Inpainting...")
rows = []
for label, les_idx in tqdm(lesions):
    bbox    = torch.tensor(test_latent_ds.bboxes[les_idx])
    caption = test_latent_ds.captions[les_idx]
    mask    = bbox_to_latent_mask(bbox)
    base    = h_lat.unsqueeze(0).float()

    inpainted     = inpaint_latent(base, mask, caption)
    inpainted_img = decode_scaled_latent(inpainted)[0]
    rows.append({'label': label, 'inpainted': inpainted_img,
                 'text': f"[{label}]\n\n{caption[:280]}", 'bbox': bbox})

fig, axes = plt.subplots(6, 3, figsize=(14, 26))
fig.suptitle(f"Inferenza 1 — Lesioni latenti da test\nBase: {h_id[:16]}… view={h_view} lat={h_side}",
             fontsize=13, y=1.01)
for c, t in enumerate(["Sana + BBox lesione", "Inpainted + Decoded", "Testo CLIP"]):
    axes[0, c].set_title(t, fontsize=10, fontweight='bold')

for r, row in enumerate(rows):
    axes[r, 0].imshow(healthy_img, cmap='gray', vmin=0, vmax=255)
    bb = row['bbox']
    if bb.sum() > 0:
        axes[r, 0].add_patch(patches.Rectangle(
            (bb[0], bb[1]), bb[2]-bb[0], bb[3]-bb[1],
            lw=2, edgecolor='red', facecolor='none'))
    axes[r, 0].set_ylabel(row['label'], fontsize=9, rotation=0, labelpad=50, va='center')
    axes[r, 1].imshow(row['inpainted'], cmap='gray', vmin=0, vmax=255)
    axes[r, 2].text(0.05, 0.95, row['text'], ha='left', va='top', fontsize=7.5,
                    transform=axes[r, 2].transAxes,
                    bbox=dict(boxstyle='round', fc='#fff9e6', alpha=0.9))
    for c in range(3): axes[r, c].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "inferenza1_overlay_test.png"), dpi=120, bbox_inches='tight')
plt.show()
print("✅ Salvato.")

"""Pure Noise Generatated Lesion"""

unet.eval(); model.eval()

mass_idx_tr = get_lesion_idx(train_latent_ds, 'mass', 3, h_view, h_side)
calc_idx_tr = get_lesion_idx(train_latent_ds, 'calc', 3, h_view, h_side)
lesions_tr  = [('Massa', i) for i in mass_idx_tr] + [('Calc.', i) for i in calc_idx_tr]
print(f"  Masse train: {[train_latent_ds.ids[i][:8] for _,i in lesions_tr[:3]]}")
print(f"  Calc. train: {[train_latent_ds.ids[i][:8] for _,i in lesions_tr[3:]]}")

print("\n⏳ Inpainting da rumore puro...")
rows_inf2 = []
for label, les_idx in tqdm(lesions_tr):
    bbox    = torch.tensor(train_latent_ds.bboxes[les_idx])
    caption = train_latent_ds.captions[les_idx]
    mask    = bbox_to_latent_mask(bbox)
    base    = h_lat.unsqueeze(0).float()
    noise   = torch.randn(1, 4, 64, 64, dtype=torch.float16)

    inpainted     = inpaint_latent(base, mask, caption, init_noise=noise)
    inpainted_img = decode_scaled_latent(inpainted)[0]
    rows_inf2.append({'label': label, 'inpainted': inpainted_img,
                      'text': f"[{label}]\n\n{caption[:280]}", 'bbox': bbox})

fig, axes = plt.subplots(6, 3, figsize=(14, 26))
fig.suptitle(f"Inferenza 2 — Rumore puro + conditioning da TRAIN\nBase: {h_id[:16]}…",
             fontsize=13, y=1.01)
for c, t in enumerate(["Sana + BBox", "Noise→Lesione (decoded)", "Testo CLIP"]):
    axes[0, c].set_title(t, fontsize=10, fontweight='bold')

for r, row in enumerate(rows_inf2):
    axes[r, 0].imshow(healthy_img, cmap='gray', vmin=0, vmax=255)
    bb = row['bbox']
    if bb.sum() > 0:
        axes[r, 0].add_patch(patches.Rectangle(
            (bb[0], bb[1]), bb[2]-bb[0], bb[3]-bb[1],
            lw=2, edgecolor='cyan', facecolor='none'))
    axes[r, 0].set_ylabel(row['label'], fontsize=9, rotation=0, labelpad=50, va='center')
    axes[r, 1].imshow(row['inpainted'], cmap='gray', vmin=0, vmax=255)
    axes[r, 2].text(0.05, 0.95, row['text'], ha='left', va='top', fontsize=7.5,
                    transform=axes[r, 2].transAxes,
                    bbox=dict(boxstyle='round', fc='#e6f0ff', alpha=0.9))
    for c in range(3): axes[r, c].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "inferenza2_purenoise_train.png"), dpi=120, bbox_inches='tight')
plt.show()
print("✅ Salvato.")

"""Sampled Latent Generation"""

unet.eval(); model.eval()

print("🧠 Caricamento immagini pixel train per VAE sampling...")
train_orig_ds = BreastDataset("train", df=df, contra_map=contra_map,
                              base_dir=LOCAL_EXTRACT_PATH)
orig_map = train_orig_ds.images_cache
print(f"  Immagini disponibili: {len(orig_map)}")

def vae_sample(img_id: str) -> torch.Tensor | None:
    arr = orig_map.get(img_id)
    if arr is None: return None
    t = torch.from_numpy(arr).unsqueeze(0).unsqueeze(0).float().to(DEVICE)
    t = t * 2.0 - 1.0
    with torch.no_grad():
        mu, logvar = model.enc(t)
        z = mu + torch.exp(0.5 * logvar.clamp(-6, 6)) * torch.randn_like(mu)
    return (z * VAE_SCALE).cpu().to(torch.float16)

print("\n⏳ VAE sampling + inpainting...")
rows_inf3 = []
for label, les_idx in tqdm(lesions_tr):
    bbox    = torch.tensor(train_latent_ds.bboxes[les_idx])
    caption = train_latent_ds.captions[les_idx]
    mask    = bbox_to_latent_mask(bbox)
    base    = h_lat.unsqueeze(0).float()
    les_id  = train_latent_ds.ids[les_idx]

    init = vae_sample(les_id)
    note = "VAE sample" if init is not None else "rumore puro (fallback)"
    if init is None:
        init = torch.randn(1, 4, 64, 64, dtype=torch.float16)
    print(f"  {label} [{les_id[:8]}] → {note}")

    inpainted     = inpaint_latent(base, mask, caption, init_noise=init)
    inpainted_img = decode_scaled_latent(inpainted)[0]
    rows_inf3.append({'label': label, 'inpainted': inpainted_img,
                      'text': f"[{label} | {note}]\n\n{caption[:260]}", 'bbox': bbox})

fig, axes = plt.subplots(6, 3, figsize=(14, 26))
fig.suptitle(f"Inferenza 3 — VAE Sample come init noise\nBase: {h_id[:16]}…",
             fontsize=13, y=1.01)
for c, t in enumerate(["Sana + BBox", "VAE Sample→Lesione (decoded)", "Testo CLIP"]):
    axes[0, c].set_title(t, fontsize=10, fontweight='bold')

for r, row in enumerate(rows_inf3):
    axes[r, 0].imshow(healthy_img, cmap='gray', vmin=0, vmax=255)
    bb = row['bbox']
    if bb.sum() > 0:
        axes[r, 0].add_patch(patches.Rectangle(
            (bb[0], bb[1]), bb[2]-bb[0], bb[3]-bb[1],
            lw=2, edgecolor='lime', facecolor='none'))
    axes[r, 0].set_ylabel(row['label'], fontsize=9, rotation=0, labelpad=50, va='center')
    axes[r, 1].imshow(row['inpainted'], cmap='gray', vmin=0, vmax=255)
    axes[r, 2].text(0.05, 0.95, row['text'], ha='left', va='top', fontsize=7.5,
                    transform=axes[r, 2].transAxes,
                    bbox=dict(boxstyle='round', fc='#e6ffe6', alpha=0.9))
    for c in range(3): axes[r, c].axis('off')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "inferenza3_vae_sample.png"), dpi=120, bbox_inches='tight')
plt.show()
print("✅ Salvato.")

"""Extended Inference with different **bbox and Textual Conditioning** on same healthy images"""

unet.eval(); model.eval()

healthy_indices = find_by_condition(test_latent_ds, 'healthy', 4)
assert len(healthy_indices) >= 4, "Meno di 4 sane nel test set!"

all_groups = []

for h_idx in healthy_indices:
    h_lat   = torch.from_numpy(test_latent_ds.latents_cache[h_idx]).float()
    h_view  = test_latent_ds.views[h_idx]
    h_side  = test_latent_ds.lateralities[h_idx]
    h_id    = test_latent_ds.ids[h_idx]
    h_img   = decode_scaled_latent(h_lat.unsqueeze(0))[0]

    mass_idx = get_lesion_idx(test_latent_ds, 'mass', 2, h_view, h_side)
    calc_idx = get_lesion_idx(test_latent_ds, 'calc', 2, h_view, h_side)
    lesions  = [('Massa',  i) for i in mass_idx] + \
               [('Calc.', i) for i in calc_idx]

    print(f"Sana {h_id[:12]}… view={h_view} lat={h_side} "
          f"| masse={[test_latent_ds.ids[i][:8] for _,i in lesions[:2]]} "
          f"| calc={[test_latent_ds.ids[i][:8] for _,i in lesions[2:]]}")

    group_results = []
    for label, les_idx in lesions:
        bbox    = torch.tensor(test_latent_ds.bboxes[les_idx])
        caption = test_latent_ds.captions[les_idx]
        mask    = bbox_to_latent_mask(bbox)
        noise   = torch.randn(1, 4, 64, 64, dtype=torch.float16)

        inpainted     = inpaint_latent(h_lat.unsqueeze(0).float(), mask,
                                       caption, init_noise=noise)
        inpainted_img = decode_scaled_latent(inpainted)[0]

        group_results.append({
            'label':    label,
            'orig':     h_img,
            'inp':      inpainted_img,
            'caption':  caption,
            'bbox':     bbox,
        })

    all_groups.append({'h_id': h_id, 'h_view': h_view,
                       'h_side': h_side, 'results': group_results})

print("\n⏳ Inpainting completato — rendering figura...")


N_HEALTHY  = len(all_groups)
N_LESIONS  = 4
N_ROWS     = N_HEALTHY * N_LESIONS

fig = plt.figure(figsize=(16, 5.5 * N_ROWS))
fig.suptitle("Inferenza 4 — Rumore puro + conditioning test (view/lat consistente)",
             fontsize=14, fontweight='bold', y=1.002)

gs = fig.add_gridspec(N_ROWS, 3,
                      width_ratios=[1, 1, 1.4],
                      hspace=0.55, wspace=0.08)

for g_idx, group in enumerate(all_groups):
    for l_idx, res in enumerate(group['results']):
        row = g_idx * N_LESIONS + l_idx

        ax_orig = fig.add_subplot(gs[row, 0])
        ax_inp  = fig.add_subplot(gs[row, 1])
        ax_txt  = fig.add_subplot(gs[row, 2])

        ax_orig.imshow(res['orig'], cmap='gray', vmin=0, vmax=255)
        bb = res['bbox']
        if bb.sum() > 0:
            ax_orig.add_patch(patches.Rectangle(
                (bb[0], bb[1]), bb[2]-bb[0], bb[3]-bb[1],
                lw=2, edgecolor='red', facecolor='none'))
        ax_orig.axis('off')

        ax_inp.imshow(res['inp'], cmap='gray', vmin=0, vmax=255)
        ax_inp.axis('off')

        if l_idx == 0:
            ax_orig.set_title(
                f"Sana originale\n{group['h_id'][:14]}… "
                f"[{group['h_view']} {group['h_side']}]",
                fontsize=8.5, fontweight='bold', pad=4)
            ax_inp.set_title("Inpainted (noise→lesione)",
                             fontsize=8.5, fontweight='bold', pad=4)
            ax_txt.set_title("Caption CLIP",
                             fontsize=8.5, fontweight='bold', pad=4)

        ax_orig.set_ylabel(res['label'], fontsize=9, fontweight='bold',
                           rotation=0, labelpad=45, va='center')

        import textwrap
        wrapped = textwrap.fill(res['caption'], width=52)
        ax_txt.text(0.04, 0.96, wrapped,
                    ha='left', va='top', fontsize=7.8,
                    transform=ax_txt.transAxes,
                    linespacing=1.4,
                    bbox=dict(boxstyle='round,pad=0.5',
                              fc='#fffbe6', ec='#ccaa00',
                              alpha=0.92, lw=1))
        ax_txt.axis('off')

        if l_idx == 0 and g_idx > 0:
            line = plt.Line2D([0.01, 0.99], [1.0, 1.0],
                              transform=ax_orig.transAxes,
                              color='#888888', linewidth=1.5,
                              linestyle='--', clip_on=False)
            ax_orig.add_line(line)

plt.savefig(os.path.join(PROJECT_ROOT, "inferenza4_4sane_4lesioni.png"),
            dpi=120, bbox_inches='tight')
plt.show()
print("✅ Figura salvata.")

"""Metrics"""

import numpy as np
import pandas as pd

print("\n" + "=" * 80)
print("INFERENCE METRICS — Tutte e 4 le tipologie di esperimenti")
print("=" * 80)

# EXP 1: Testing Latent Transfer
print("\n\n🔹 ESPERIMENTO 1: Lesioni Latenti da Test (inferenza1)")
print("-" * 80)

exp1_gen = np.array([row[3] for row in results])
exp1_gt  = np.array([row[2] for row in results])

print(f"📊 Campioni: {len(exp1_gen)}")

ssim1_mean, ssim1_std = compute_ssim_batch(exp1_gt, exp1_gen, data_range=255)
features_gt1  = fid_calc.extract_features(exp1_gt)
features_gen1 = fid_calc.extract_features(exp1_gen)
fid1_score = fid_calc.compute_fid(features_gt1, features_gen1)

print(f"   SSIM: {ssim1_mean:.4f} (±{ssim1_std:.4f})")
print(f"   FID:  {fid1_score:.2f}")

# EXP 2: Pure Noise Generation
print("\n\n🔹 ESPERIMENTO 2: Rumore Puro + Conditioning Train (inferenza2)")
print("-" * 80)

exp2_gen = np.array([row['inpainted'] for row in rows_inf2])

exp2_gt = np.array([
    decode_scaled_latent(
        torch.from_numpy(train_latent_ds.latents_cache[i]).unsqueeze(0).float()
    )[0]
    for _, i in lesions_tr
])

print(f"📊 Campioni: {len(exp2_gen)}")

ssim2_mean, ssim2_std = compute_ssim_batch(exp2_gt, exp2_gen, data_range=255)
features_gt2  = fid_calc.extract_features(exp2_gt)
features_gen2 = fid_calc.extract_features(exp2_gen)
fid2_score = fid_calc.compute_fid(features_gt2, features_gen2)

print(f"   SSIM: {ssim2_mean:.4f} (±{ssim2_std:.4f})")
print(f"   FID:  {fid2_score:.2f}")

# EXP 3: VAE Sample as Init Noise
print("\n\n🔹 ESPERIMENTO 3: VAE Sample come Init Noise (inferenza3)")
print("-" * 80)

exp3_gen = np.array([row['inpainted'] for row in rows_inf3])

exp3_gt = np.array([
    decode_scaled_latent(
        torch.from_numpy(train_latent_ds.latents_cache[i]).unsqueeze(0).float()
    )[0]
    for _, i in lesions_tr
])

print(f"📊 Campioni: {len(exp3_gen)}")

ssim3_mean, ssim3_std = compute_ssim_batch(exp3_gt, exp3_gen, data_range=255)
features_gt3  = fid_calc.extract_features(exp3_gt)
features_gen3 = fid_calc.extract_features(exp3_gen)
fid3_score = fid_calc.compute_fid(features_gt3, features_gen3)

print(f"   SSIM: {ssim3_mean:.4f} (±{ssim3_std:.4f})")
print(f"   FID:  {fid3_score:.2f}")

# EXP 4: 4 Healthy + Lesion Conditioning (inferenza4)
print("\n\n🔹 ESPERIMENTO 4: 4 Sane × Lesioni (inferenza4)")
print("-" * 80)

exp4_gen_list = []
exp4_gt_list  = []

for group in all_groups:
    for res in group['results']:
        exp4_gen_list.append(res['inp'])

        lesion_type = 'mass' if res['label'] == 'Massa' else 'calc'
        lesion_idx_list = find_by_condition(test_latent_ds, lesion_type, 1)

        if lesion_idx_list:
            lesion_idx = lesion_idx_list[0]
            gt_decoded = decode_scaled_latent(
                torch.from_numpy(test_latent_ds.latents_cache[lesion_idx]).unsqueeze(0).float()
            )[0]
            exp4_gt_list.append(gt_decoded)
        else:
            exp4_gt_list.append(res['inp'].copy())

exp4_gen = np.array(exp4_gen_list)
exp4_gt  = np.array(exp4_gt_list)

print(f"📊 Campioni: {len(exp4_gen)} (4 healthy × {len(all_groups[0]['results'])} lesioni)")

ssim4_mean, ssim4_std = compute_ssim_batch(exp4_gt, exp4_gen, data_range=255)
features_gt4  = fid_calc.extract_features(exp4_gt)
features_gen4 = fid_calc.extract_features(exp4_gen)
fid4_score = fid_calc.compute_fid(features_gt4, features_gen4)

print(f"   SSIM: {ssim4_mean:.4f} (±{ssim4_std:.4f})")
print(f"   FID:  {fid4_score:.2f}")

# SUMMARY TABLE
print("\n\n" + "=" * 80)
print("📈 RIEPILOGO FINALE")
print("=" * 80)

summary_df = pd.DataFrame({
    'Esperimento': [
        'Exp 1: Testing Latent',
        'Exp 2: Pure Noise',
        'Exp 3: VAE Sample',
        'Exp 4: 4 Healthy'
    ],
    'SSIM': [
        f'{ssim1_mean:.4f}±{ssim1_std:.4f}',
        f'{ssim2_mean:.4f}±{ssim2_std:.4f}',
        f'{ssim3_mean:.4f}±{ssim3_std:.4f}',
        f'{ssim4_mean:.4f}±{ssim4_std:.4f}'
    ],
    'FID': [
        f'{fid1_score:.2f}',
        f'{fid2_score:.2f}',
        f'{fid3_score:.2f}',
        f'{fid4_score:.2f}'
    ],
    'Best?': [
        '⭐ SSIM' if ssim1_mean == max(ssim1_mean, ssim2_mean, ssim3_mean, ssim4_mean) else '',
        '⭐ SSIM' if ssim2_mean == max(ssim1_mean, ssim2_mean, ssim3_mean, ssim4_mean) else '',
        '⭐ SSIM' if ssim3_mean == max(ssim1_mean, ssim2_mean, ssim3_mean, ssim4_mean) else '',
        '⭐ SSIM' if ssim4_mean == max(ssim1_mean, ssim2_mean, ssim3_mean, ssim4_mean) else ''
    ]
})

print(summary_df.to_string(index=False))

print("=" * 80)
print(f"\n🎯 Esperimento migliore complessivamente:")

scores = [
    (1, ssim1_mean, fid1_score),
    (2, ssim2_mean, fid2_score),
    (3, ssim3_mean, fid3_score),
    (4, ssim4_mean, fid4_score)
]

composite = [(i, s + (100-f)/100) for i, s, f in scores]
best_exp = max(composite, key=lambda x: x[1])

print(f"   Exp {int(best_exp[0])} (score composito: {best_exp[1]:.3f})")
print("\n✅ Metriche completate su tutti gli esperimenti.")

"""Real Global Evaluation, this is considered the real variance-free evaluation."""

import numpy as np
import pandas as pd
from tqdm import tqdm
import torch

print("\n" + "=" * 100)
print("DUAL TESTING STRATEGY — Pure Noise Generation vs Lesion Transfer")
print("Applying lesions to contralateral healthy breasts")
print("=" * 100)

unet.eval()
model.eval()

mass_indices = find_by_condition(test_latent_ds, 'mass', 999)
calc_indices = find_by_condition(test_latent_ds, 'calc', 999)

print(f"\nDataset Overview:")
print(f"  Masses available:              {len(mass_indices)}")
print(f"  Calcifications available:      {len(calc_indices)}")
print(f"  Total lesions:                 {len(mass_indices) + len(calc_indices)}")

@torch.no_grad()
def decode_latent_to_uint8(latent_scaled: torch.Tensor) -> np.ndarray:
    lat = (latent_scaled.to(DEVICE) / VAE_SCALE).float()
    if lat.dim() == 3:
        lat = lat.unsqueeze(0)
    imgs = model.dec(lat)
    return (((imgs.cpu().numpy()[0, 0] + 1.0) / 2.0) * 255).clip(0, 255).astype(np.uint8)

def get_contralateral_latent(lesion_idx, dataset, contra_map):
    img_id = dataset.ids[lesion_idx]
    row = df[df['image_id'].astype(str).str.replace('.png', '', regex=False) == img_id].iloc[0]
    patient_id = row['patient_id']
    view = row['view']
    current_side = row['laterality']
    other_side = 'R' if current_side == 'L' else 'L'

    contra_id = contra_map.get((patient_id, view), {}).get(other_side)
    if contra_id and contra_id in dataset.ids:
        contra_idx = dataset.ids.index(str(contra_id).replace('.png', ''))
        return torch.from_numpy(dataset.latents_cache[contra_idx]).unsqueeze(0).float(), contra_idx
    return None, None

print("\n" + "=" * 100)
print("TEST 1: PURE NOISE GENERATION")
print("Generating lesions on contralateral healthy breast using pure noise")
print("=" * 100)

test1_results = {
    'Mass': {'gt': [], 'gen': [], 'bboxes': []},
    'Calc': {'gt': [], 'gen': [], 'bboxes': []}
}

print(f"\nPhase 1: Masses - Pure Noise Generation\n")

mass_count = 0
for mass_idx in tqdm(mass_indices, desc="Processing masses", unit="lesion"):
    contra_latent, contra_idx = get_contralateral_latent(mass_idx, test_latent_ds, contra_map)

    if contra_latent is None:
        continue

    gt_img = decode_latent_to_uint8(contra_latent[0])

    mass_bbox = torch.tensor(test_latent_ds.bboxes[mass_idx])
    mass_caption = test_latent_ds.captions[mass_idx]

    if mass_bbox.sum() > 0:
        mask = bbox_to_latent_mask(mass_bbox)
        noise = torch.randn(1, 4, 64, 64, dtype=torch.float16)
        inpainted = inpaint_latent(contra_latent, mask, mass_caption, init_noise=noise)
        gen_img = decode_latent_to_uint8(inpainted[0])
    else:
        gen_img = gt_img.copy()

    test1_results['Mass']['gt'].append(gt_img)
    test1_results['Mass']['gen'].append(gen_img)
    test1_results['Mass']['bboxes'].append(mass_bbox.numpy())

    mass_count += 1
    torch.cuda.empty_cache()

print(f"Successfully generated: {mass_count} masses on contralateral breasts")

print(f"\nPhase 2: Calcifications - Pure Noise Generation\n")

calc_count = 0
for calc_idx in tqdm(calc_indices, desc="Processing calcifications", unit="lesion"):
    contra_latent, contra_idx = get_contralateral_latent(calc_idx, test_latent_ds, contra_map)

    if contra_latent is None:
        continue

    gt_img = decode_latent_to_uint8(contra_latent[0])

    calc_bbox = torch.tensor(test_latent_ds.bboxes[calc_idx])
    calc_caption = test_latent_ds.captions[calc_idx]

    if calc_bbox.sum() > 0:
        mask = bbox_to_latent_mask(calc_bbox)
        noise = torch.randn(1, 4, 64, 64, dtype=torch.float16)
        inpainted = inpaint_latent(contra_latent, mask, calc_caption, init_noise=noise)
        gen_img = decode_latent_to_uint8(inpainted[0])
    else:
        gen_img = gt_img.copy()

    test1_results['Calc']['gt'].append(gt_img)
    test1_results['Calc']['gen'].append(gen_img)
    test1_results['Calc']['bboxes'].append(calc_bbox.numpy())

    calc_count += 1
    torch.cuda.empty_cache()

print(f"Successfully generated: {calc_count} calcifications on contralateral breasts")

for lesion_type in ['Mass', 'Calc']:
    test1_results[lesion_type]['gt'] = np.array(test1_results[lesion_type]['gt'])
    test1_results[lesion_type]['gen'] = np.array(test1_results[lesion_type]['gen'])
    test1_results[lesion_type]['bboxes'] = np.array(test1_results[lesion_type]['bboxes'])

print(f"\nTEST 1 Summary:")
print(f"  Masses:            {len(test1_results['Mass']['gt'])} samples")
print(f"  Calcifications:    {len(test1_results['Calc']['gt'])} samples")

print("\n" + "=" * 100)
print("TEST 2: LESION TRANSFER")
print("Transferring lesions from pathological to contralateral healthy breast")
print("=" * 100)

test2_results = {
    'Mass': {'gt': [], 'gen': [], 'lesion_img': []},
    'Calc': {'gt': [], 'gen': [], 'lesion_img': []}
}

print(f"\nPhase 1: Masses - Lesion Transfer\n")

mass_transfer_count = 0
for mass_idx in tqdm(mass_indices, desc="Processing masses", unit="lesion"):
    contra_latent, contra_idx = get_contralateral_latent(mass_idx, test_latent_ds, contra_map)

    if contra_latent is None:
        continue

    gt_img = decode_latent_to_uint8(contra_latent[0])

    mass_latent = torch.from_numpy(test_latent_ds.latents_cache[mass_idx]).unsqueeze(0).float()
    mass_bbox = torch.tensor(test_latent_ds.bboxes[mass_idx])
    mass_caption = test_latent_ds.captions[mass_idx]
    lesion_img = decode_latent_to_uint8(mass_latent[0])

    if mass_bbox.sum() > 0:
        mask = bbox_to_latent_mask(mass_bbox)
        inpainted = inpaint_latent(contra_latent, mask, mass_caption, init_noise=mass_latent)
        gen_img = decode_latent_to_uint8(inpainted[0])
    else:
        gen_img = gt_img.copy()

    test2_results['Mass']['gt'].append(gt_img)
    test2_results['Mass']['gen'].append(gen_img)
    test2_results['Mass']['lesion_img'].append(lesion_img)

    mass_transfer_count += 1
    torch.cuda.empty_cache()

print(f"Successfully transferred: {mass_transfer_count} masses to contralateral breasts")

print(f"\nPhase 2: Calcifications - Lesion Transfer\n")

calc_transfer_count = 0
for calc_idx in tqdm(calc_indices, desc="Processing calcifications", unit="lesion"):
    contra_latent, contra_idx = get_contralateral_latent(calc_idx, test_latent_ds, contra_map)

    if contra_latent is None:
        continue

    gt_img = decode_latent_to_uint8(contra_latent[0])

    calc_latent = torch.from_numpy(test_latent_ds.latents_cache[calc_idx]).unsqueeze(0).float()
    calc_bbox = torch.tensor(test_latent_ds.bboxes[calc_idx])
    calc_caption = test_latent_ds.captions[calc_idx]
    lesion_img = decode_latent_to_uint8(calc_latent[0])

    if calc_bbox.sum() > 0:
        mask = bbox_to_latent_mask(calc_bbox)
        inpainted = inpaint_latent(contra_latent, mask, calc_caption, init_noise=calc_latent)
        gen_img = decode_latent_to_uint8(inpainted[0])
    else:
        gen_img = gt_img.copy()

    test2_results['Calc']['gt'].append(gt_img)
    test2_results['Calc']['gen'].append(gen_img)
    test2_results['Calc']['lesion_img'].append(lesion_img)

    calc_transfer_count += 1
    torch.cuda.empty_cache()

print(f"Successfully transferred: {calc_transfer_count} calcifications to contralateral breasts")

for lesion_type in ['Mass', 'Calc']:
    test2_results[lesion_type]['gt'] = np.array(test2_results[lesion_type]['gt'])
    test2_results[lesion_type]['gen'] = np.array(test2_results[lesion_type]['gen'])
    test2_results[lesion_type]['lesion_img'] = np.array(test2_results[lesion_type]['lesion_img'])

print(f"\nTEST 2 Summary:")
print(f"  Masses:            {len(test2_results['Mass']['gt'])} samples")
print(f"  Calcifications:    {len(test2_results['Calc']['gt'])} samples")

print("\n" + "=" * 100)
print("METRICS COMPUTATION")
print("=" * 100)

def compute_metrics_batch(test_name, lesion_type, gt_batch, gen_batch, fid_calc):
    ssim_mean, ssim_std = compute_ssim_batch(gt_batch, gen_batch, data_range=255)
    features_gt  = fid_calc.extract_features(gt_batch)
    features_gen = fid_calc.extract_features(gen_batch)
    fid_score = fid_calc.compute_fid(features_gt, features_gen)

    return {
        'test': test_name,
        'lesion_type': lesion_type,
        'count': len(gt_batch),
        'ssim_mean': ssim_mean,
        'ssim_std': ssim_std,
        'fid': fid_score
    }

metrics_results = []

print("\nTEST 1: PURE NOISE GENERATION")
print("-" * 100)

for lesion_type in ['Mass', 'Calc']:
    gt = test1_results[lesion_type]['gt']
    gen = test1_results[lesion_type]['gen']

    if len(gt) > 0:
        print(f"\nProcessing {lesion_type} (n={len(gt)})...", end=" ", flush=True)
        result = compute_metrics_batch('Pure Noise', lesion_type, gt, gen, fid_calc)
        metrics_results.append(result)
        print(f"SSIM={result['ssim_mean']:.4f} | FID={result['fid']:.2f}")

print("\n\nTEST 2: LESION TRANSFER")
print("-" * 100)

for lesion_type in ['Mass', 'Calc']:
    gt = test2_results[lesion_type]['gt']
    gen = test2_results[lesion_type]['gen']

    if len(gt) > 0:
        print(f"\nProcessing {lesion_type} (n={len(gt)})...", end=" ", flush=True)
        result = compute_metrics_batch('Lesion Transfer', lesion_type, gt, gen, fid_calc)
        metrics_results.append(result)
        print(f"SSIM={result['ssim_mean']:.4f} | FID={result['fid']:.2f}")

print("\n" + "=" * 100)
print("RESULTS TABLE")
print("=" * 100 + "\n")

summary_df = pd.DataFrame([
    {
        'Test': r['test'],
        'Lesion Type': r['lesion_type'],
        'Samples': r['count'],
        'SSIM': f"{r['ssim_mean']:.4f}±{r['ssim_std']:.4f}",
        'FID': f"{r['fid']:.2f}"
    }
    for r in metrics_results
])

print(summary_df.to_string(index=False))

print("\n" + "=" * 100)
print("COMPARATIVE ANALYSIS: PURE NOISE vs LESION TRANSFER")
print("=" * 100 + "\n")

def compute_composite_score(ssim, fid):
    ssim_norm = ssim * 50
    fid_norm = max(0, 50 - (fid / 2))
    return ssim_norm + fid_norm

comparison_data = []

for lesion_type in ['Mass', 'Calc']:
    pure_noise = next((r for r in metrics_results if r['test'] == 'Pure Noise' and r['lesion_type'] == lesion_type), None)
    transfer = next((r for r in metrics_results if r['test'] == 'Lesion Transfer' and r['lesion_type'] == lesion_type), None)

    if pure_noise and transfer:
        pn_score = compute_composite_score(pure_noise['ssim_mean'], pure_noise['fid'])
        tr_score = compute_composite_score(transfer['ssim_mean'], transfer['fid'])

        comparison_data.append({
            'Lesion Type': lesion_type,
            'Pure Noise Score': f"{pn_score:.1f}",
            'Transfer Score': f"{tr_score:.1f}",
            'Better Method': 'Pure Noise' if pn_score > tr_score else 'Transfer',
            'Margin': f"{abs(pn_score - tr_score):.1f}"
        })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))

print("\n" + "-" * 100)
print("INTERPRETATION")
print("-" * 100 + "\n")

for lesion_type in ['Mass', 'Calc']:
    pure_noise = next((r for r in metrics_results if r['test'] == 'Pure Noise' and r['lesion_type'] == lesion_type), None)
    transfer = next((r for r in metrics_results if r['test'] == 'Lesion Transfer' and r['lesion_type'] == lesion_type), None)

    if pure_noise and transfer:
        pn_score = compute_composite_score(pure_noise['ssim_mean'], pure_noise['fid'])
        tr_score = compute_composite_score(transfer['ssim_mean'], transfer['fid'])

        print(f"{lesion_type}:")
        print(f"  Pure Noise:       SSIM={pure_noise['ssim_mean']:.4f} | FID={pure_noise['fid']:.2f} | Score={pn_score:.1f}")
        print(f"  Lesion Transfer:  SSIM={transfer['ssim_mean']:.4f} | FID={transfer['fid']:.2f} | Score={tr_score:.1f}")

        if pn_score > tr_score:
            print(f"  Best: Pure Noise (+{abs(pn_score - tr_score):.1f} points)")
        else:
            print(f"  Best: Lesion Transfer (+{abs(pn_score - tr_score):.1f} points)")

print("=" * 100)
print("GLOBAL AGGREGATE SCORES")
print("=" * 100 + "\n")

global_metrics = {}

for test_name in ['Pure Noise', 'Lesion Transfer']:
    test_results = [r for r in metrics_results if r['test'] == test_name]

    if test_results:
        avg_ssim = np.mean([r['ssim_mean'] for r in test_results])
        avg_fid = np.mean([r['fid'] for r in test_results])
        global_score = compute_composite_score(avg_ssim, avg_fid)

        global_metrics[test_name] = {
            'avg_ssim': avg_ssim,
            'avg_fid': avg_fid,
            'score': global_score,
            'n_total': sum(r['count'] for r in test_results)
        }

best_test = max(global_metrics.items(), key=lambda x: x[1]['score'])

for test_name, metrics in sorted(global_metrics.items(), key=lambda x: x[1]['score'], reverse=True):
    rank = "BEST" if test_name == best_test[0] else "SECOND"
    print(f"{rank}: {test_name}")
    print(f"  SSIM Average:        {metrics['avg_ssim']:.4f}")
    print(f"  FID Average:         {metrics['avg_fid']:.2f}")
    print(f"  Global Score:        {metrics['score']:.1f}/100")
    print(f"  Total Samples:       {metrics['n_total']}\n")

print("=" * 100)
print("CONCLUSION")
print("=" * 100 + "\n")

print(f"Overall Winner: {best_test[0]}")
print(f"Score: {best_test[1]['score']:.1f}/100\n")

if best_test[0] == 'Pure Noise':
    print("Summary:  The model excels at generating synthetic lesions from pure noise.")
else:
    print("Summary:  The model performs better at transferring real lesion characteristics.")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100 + "\n")

"""### Baseline

Our Pipeline vs Vanilla Complete
"""

import gc
from diffusers import StableDiffusionInpaintPipeline

unet.eval(); model.eval()

print("🔄 Caricamento SD Vanilla pipeline...")
pipe_v = StableDiffusionInpaintPipeline.from_pretrained(
    MODEL_ID, torch_dtype=torch.float16, safety_checker=None
).to(DEVICE)
pipe_v.set_progress_bar_config(disable=True)
print(f"✅ Vanilla pronta. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

b1_idx = (
    find_by_condition(test_latent_ds, 'mass',    2) +
    find_by_condition(test_latent_ds, 'calc',    2) +
    find_by_condition(test_latent_ds, 'healthy', 4)
)[:8]

def to_pil(img_np: np.ndarray) -> Image.Image:
    return Image.fromarray(img_np, mode='L').convert('RGB')

def bbox_to_pil_mask(bbox: torch.Tensor, size: int = 512) -> Image.Image:
    m = Image.new('L', (size, size), 0)
    if bbox.sum() > 0:
        d = ImageDraw.Draw(m)
        x0,y0,x1,y1 = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
        if x1>x0 and y1>y0: d.rectangle([x0,y0,x1,y1], fill=255)
    return m

print(f"\n⏳ Running {len(b1_idx)} campioni su entrambe le pipeline...")
rows_b1 = []

for idx in tqdm(b1_idx):
    latent_t = torch.from_numpy(test_latent_ds.latents_cache[idx]).unsqueeze(0).float()
    bbox     = torch.tensor(test_latent_ds.bboxes[idx])
    caption  = test_latent_ds.captions[idx]
    mask_lat = bbox_to_latent_mask(bbox)
    cond     = test_latent_ds.conditions[idx]
    orig_img = decode_scaled_latent(latent_t)[0]

    noise       = torch.randn(1, 4, 64, 64, dtype=torch.float16)
    inp_ours    = inpaint_latent(latent_t, mask_lat, caption, init_noise=noise.clone())
    our_img     = decode_scaled_latent(inp_ours)[0]

    mask_pil = bbox_to_pil_mask(bbox)
    if bbox.sum() == 0:
        m = Image.new('L', (512,512), 0); d = ImageDraw.Draw(m)
        d.ellipse([100,100,400,400], fill=128); mask_pil = m
    van_out  = pipe_v(prompt=caption, image=to_pil(orig_img), mask_image=mask_pil,
                      height=512, width=512, num_inference_steps=NUM_INFERENCE_STEPS,
                      guidance_scale=GUIDANCE_SCALE).images[0]
    van_img  = np.array(van_out.convert('L'))

    label = 'M' if cond[0] else ('C' if cond[1] else 'S')
    rows_b1.append({'orig': orig_img, 'ours': our_img, 'vanilla': van_img,
                    'text': caption[:250], 'bbox': bbox, 'label': label})

n = len(rows_b1)
fig, axes = plt.subplots(n, 4, figsize=(18, 5*n))
if n == 1: axes = axes[np.newaxis,:]
fig.suptitle("Baseline 1 — Nostra Pipeline vs SD Vanilla\n(M=Massa, C=Calc., S=Sana)",
             fontsize=13, y=1.01)
for c, t in enumerate(["Originale (decoded)", "Nostra (LoRA+CustomVAE)",
                        "SD Vanilla (pixel space)", "Testo CLIP"]):
    axes[0, c].set_title(t, fontsize=10, fontweight='bold')

for r, row in enumerate(rows_b1):
    for c, key in enumerate(['orig', 'ours', 'vanilla']):
        axes[r,c].imshow(row[key], cmap='gray', vmin=0, vmax=255)
        axes[r,c].axis('off')
        bb = row['bbox']
        if bb.sum() > 0:
            axes[r,c].add_patch(patches.Rectangle(
                (bb[0],bb[1]), bb[2]-bb[0], bb[3]-bb[1],
                lw=1.5, edgecolor='red', facecolor='none'))
    axes[r, 3].text(0.05, 0.95, row['text'], ha='left', va='top', fontsize=7,
                    transform=axes[r,3].transAxes,
                    bbox=dict(boxstyle='round', fc='#fff9e6', alpha=0.9))
    axes[r, 3].axis('off')
    axes[r, 0].set_ylabel(row['label'], fontsize=11, rotation=0,
                           labelpad=30, va='center', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "baseline1_vs_vanilla.png"), dpi=120, bbox_inches='tight')
plt.show()

del pipe_v; gc.collect(); torch.cuda.empty_cache()
print("✅ Salvato. Vanilla rimossa dalla VRAM.")

"""Our denoiser vs Vanilla Denoiser"""

from diffusers import UNet2DConditionModel

unet.eval(); model.eval()

b2_h_idx    = find_by_condition(test_latent_ds, 'healthy', 1)[0]
b2_h_lat    = torch.from_numpy(test_latent_ds.latents_cache[b2_h_idx]).float()
b2_h_view   = test_latent_ds.views[b2_h_idx]
b2_h_side   = test_latent_ds.lateralities[b2_h_idx]
b2_h_id     = test_latent_ds.ids[b2_h_idx]
b2_healthy  = decode_scaled_latent(b2_h_lat.unsqueeze(0))[0]
print(f"Sana: {b2_h_id[:16]}…  view={b2_h_view}  lat={b2_h_side}")

b2_mass = get_lesion_idx(test_latent_ds, 'mass', 3, b2_h_view, b2_h_side)
b2_calc = get_lesion_idx(test_latent_ds, 'calc', 3, b2_h_view, b2_h_side)
b2_les  = [('Massa', i) for i in b2_mass] + [('Calc.', i) for i in b2_calc]

print("\n🔄 Caricamento UNet Vanilla...")
unet_vanilla = UNet2DConditionModel.from_pretrained(
    MODEL_ID, subfolder="unet", torch_dtype=torch.float16
).to(DEVICE)
unet_vanilla.eval()
print(f"✅ UNet Vanilla pronta. VRAM: {torch.cuda.memory_allocated()/1e9:.2f} GB")

print("\n⏳ LoRA vs Vanilla UNet...")
rows_b2 = []
for label, les_idx in tqdm(b2_les):
    bbox    = torch.tensor(test_latent_ds.bboxes[les_idx])
    caption = test_latent_ds.captions[les_idx]
    mask    = bbox_to_latent_mask(bbox)
    base    = b2_h_lat.unsqueeze(0).float()
    noise   = torch.randn(1, 4, 64, 64, dtype=torch.float16)

    img_lora = decode_scaled_latent(
        inpaint_latent(base, mask, caption,
                       unet_model=unet,         init_noise=noise.clone()))[0]
    img_van  = decode_scaled_latent(
        inpaint_latent(base, mask, caption,
                       unet_model=unet_vanilla, init_noise=noise.clone()))[0]

    rows_b2.append({'label': label, 'lora': img_lora, 'vanilla': img_van,
                    'text': f"[{label}]\n\n{caption[:260]}", 'bbox': bbox})

n = len(rows_b2)
fig, axes = plt.subplots(n, 4, figsize=(18, 5*n))
if n == 1: axes = axes[np.newaxis,:]
fig.suptitle("Baseline 2 — LoRA Finetuned vs UNet Vanilla\n"
             "(stesso rumore, stesso custom VAE decoder)",
             fontsize=13, y=1.01)
for c, t in enumerate(["Sana (decoded)", "LoRA Finetuned",
                        "UNet Vanilla", "Testo CLIP"]):
    axes[0, c].set_title(t, fontsize=10, fontweight='bold')

for r, row in enumerate(rows_b2):
    axes[r, 0].imshow(b2_healthy,      cmap='gray', vmin=0, vmax=255)
    axes[r, 1].imshow(row['lora'],     cmap='gray', vmin=0, vmax=255)
    axes[r, 2].imshow(row['vanilla'],  cmap='gray', vmin=0, vmax=255)
    axes[r, 3].text(0.05, 0.95, row['text'], ha='left', va='top', fontsize=7.5,
                    transform=axes[r,3].transAxes,
                    bbox=dict(boxstyle='round', fc='#ffe6e6', alpha=0.9))
    axes[r, 3].axis('off')
    axes[r, 0].set_ylabel(row['label'], fontsize=9, rotation=0,
                           labelpad=50, va='center', fontweight='bold')
    bb = row['bbox']
    for c in range(3):
        axes[r, c].axis('off')
        if bb.sum() > 0:
            axes[r, c].add_patch(patches.Rectangle(
                (bb[0], bb[1]), bb[2]-bb[0], bb[3]-bb[1],
                lw=2, edgecolor='yellow', facecolor='none'))

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, "baseline2_lora_vs_vanilla.png"), dpi=120, bbox_inches='tight')
plt.show()

del unet_vanilla; gc.collect(); torch.cuda.empty_cache()
print("✅ Salvato. Vanilla UNet rimossa dalla VRAM.")