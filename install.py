import launch

if not launch.is_installed("diskcache"):
    launch.run_pip("install diskcache~=5.6.0", "for i2i Ancestral Tree")
