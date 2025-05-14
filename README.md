# Sora no Kiseki 3rd PSP -- Base Patch

**tools/ppsspp-virtfs-tools** -> to create `.ppsspp-index.lst`. Place this folder on the root disc folder.

**original** -> folder that contains original files.

**filelist.txt** -> Exported from UMDgen

**disc** -> the disc content

start.dat -> `dat_read.py` (with `falcom_decompress_v2`)
*.vag -> ffmpeg: adpcm_psx
*.pmf -> ffmpeg: h264

# PPSSPP Works

__KernelSetupRootThread

* allocation Stack and set SP regsiter


calling by: 0x088041e8
user_main start:	0x08804228

sceIoOpenAsync
sceIoPollAsync
sceIoLseekAsync
sceIoReadAsync
sceIoWaitAsyncCB

For Opening file, Breakpoint at `VirtualDiscFileSystem::OpenFile`

0. open data.lst
  pc	u32	0x089eee1c
  r[29]/sp	u32	0x09fff490

1. disc0:/sce_lbn0e57b_size0x7a7800
  size: 8026112
  sector: 58747
  idx: 10079
  ofs: 0

  ffplay -i disc/PSP_GAME/USRDIR/data_3rd/movie/ed6_logo.pmf


2. disc0:/sce_lbn02cc3e_size0x1e0d38
  fileIndex 2534
  size 1969464
  sector 183358
  ofs 0
  ffplay -i disc/PSP_GAME/USRDIR/data_3rd/bgm/ed6574.at3

3. disc0:/sce_lbn0f4ca_size0x234330
  sectorStart	u32	62666
  readSize	u32	2310960
  fileIndex	int	2434
  ffplay -i disc/PSP_GAME/USRDIR/data_3rd/bgm/ed6020.at3
## File Format

* bgm/*.at3 --> ffmpeg Audio: atrac3p, 44100 Hz, stereo, fltp, 128 kb/s
* movie/*.pmf --> ffmpeg Video: h264 (Main), yuv420p(tv, progressive), 480x272 [SAR 1:1 DAR 30:17], 29.97 fps
* start.dat, joutyu.dat --> `dat_read.py` (with `falcom_decompress_v2`)
