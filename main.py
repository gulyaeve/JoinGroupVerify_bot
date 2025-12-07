from bot.app import launch_polling
# from bot.app import launch_webhook
from asyncio import run

# def main():
#     print("Hello from videoround-bot!")


if __name__ == "__main__":
    run(launch_polling())
    # launch_webhook()
