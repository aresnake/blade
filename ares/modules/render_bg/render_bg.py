"""
Blade v13 — render_bg (squelette)
- Configure la sortie vidéo (FFMPEG mp4 H.264 + AAC) de manière robuste.
- Ne lance PAS de rendu ici (smoke only).
"""
import bpy
import json
from pathlib import Path

def _safe_set(obj, prop, val):
    try:
        if hasattr(obj, prop):
            setattr(obj, prop, val)
            return True
    except Exception:
        pass
    return False

def _set_if_in(obj, prop, val, allowed):
    if val in allowed:
        return _safe_set(obj, prop, val)
    return False

def apply_output_preset(config_path: str = "config/render_output_defaults.yaml") -> dict:
    """
    Applique un preset de sortie FFMPEG (mp4 H.264 + AAC) si possible.
    Retourne un dict de ce qui a été réglé pour log/smoke.
    """
    scene = bpy.context.scene
    out = scene.render
    res = {}

    # 1) Lire la config YAML (fallback JSON minimal si YAML indispo)
    data = {}
    p = Path(bpy.path.abspath("//")) / config_path if "//" in config_path else Path(config_path)
    try:
        import yaml  # type: ignore
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        # fallback très simple si yaml absent : on encode un preset par défaut
        data = {
            "format": "FFMPEG",
            "filepath": "//renders/out.mp4",
            "use_file_extension": True,
            "ffmpeg": {"format": "MPEG4", "codec": "H264", "audio_codec": "AAC", "ffmpeg_preset": "GOOD"},
            "video": {"bitrate": 8000, "maxrate": 12000, "gopsize": 12},
            "audio": {"use_audio": True, "audio_mixrate": 48000, "audio_channels": "STEREO", "audio_bitrate": 192},
        }

    # 2) Format rendu = FFMPEG (si dispo)
    _safe_set(out, "image_settings.file_format", data.get("format", "FFMPEG"))
    res["file_format"] = getattr(out.image_settings, "file_format", None)

    # 3) Filepath + extension
    _safe_set(out, "filepath", data.get("filepath", "//renders/out.mp4"))
    _safe_set(out, "use_file_extension", bool(data.get("use_file_extension", True)))
    res["filepath"] = out.filepath

    # 4) FFmpeg
    ff = getattr(scene.render, "ffmpeg", None)
    if ff:
        # conteneur
        _set_if_in(ff, "format", data.get("ffmpeg", {}).get("format", "MPEG4"),
                   {"MPEG4","MKV","QUICKTIME","AVI","WEBM","OGG"})
        # codec vidéo
        _set_if_in(ff, "codec", data.get("ffmpeg", {}).get("codec", "H264"),
                   {"H264","MPEG4","HEVC","VP9","THEORA"})
        # preset ffmpeg
        _set_if_in(ff, "ffmpeg_preset", data.get("ffmpeg", {}).get("ffmpeg_preset", "GOOD"),
                   {"BEST","GOOD","REALTIME","NONE"})
        # rate control
        _set_if_in(ff, "constant_rate_factor", data.get("ffmpeg", {}).get("constant_rate_factor", "MEDIUM"),
                   {"LOWEST","LOW","MEDIUM","HIGH","PERC_LOSSLESS","LOSSLESS"})
        # audio
        _set_if_in(ff, "audio_codec", data.get("ffmpeg", {}).get("audio_codec", "AAC"),
                   {"AAC","MP3","OPUS","VORBIS","PCM","FLAC"})
        res["ffmpeg"] = {
            "format": getattr(ff, "format", None),
            "codec": getattr(ff, "codec", None),
            "preset": getattr(ff, "ffmpeg_preset", None),
            "crf": getattr(ff, "constant_rate_factor", None),
            "audio_codec": getattr(ff, "audio_codec", None),
        }

    # 5) Video rates (best effort)
    for k, v in (data.get("video") or {}).items():
        _safe_set(out, k, v)

    # 6) Audio master
    if data.get("audio", {}).get("use_audio", True) and hasattr(scene, "audio_settings"):
        au = scene.audio_settings
        _safe_set(au, "mixrate", int(data["audio"].get("audio_mixrate", 48000)))
        # channels enum strict
        _set_if_in(au, "channels", data["audio"].get("audio_channels", "STEREO"),
                   {"MONO","STEREO","SURROUND51","SURROUND71"})
        res["audio"] = {
            "mixrate": getattr(au, "mixrate", None),
            "channels": getattr(au, "channels", None),
        }

    return res
