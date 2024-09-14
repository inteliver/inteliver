import os


def define_env(env):
    # Define your environment variables
    media_base = os.getenv("MEDIA_BASE", "http://res.inteliver.local")
    cloud_name = os.getenv("CLOUD_NAME", "inteliver")

    # Add your variables to the environment
    env.variables["mediaBase"] = media_base
    env.variables["cloudName"] = cloud_name
