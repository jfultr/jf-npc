def read_api_key(env_name: str):
    import os
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(env_name)

