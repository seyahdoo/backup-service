import rclone
from mail import send_mail_to_myself


def main():
    # send_mail_to_myself("ERROR on Backup Service", "Error")
    rclone.copy("C:/Users/kardan/Videos", "gdrive:Rsync/Beast/Videos")
    return


if __name__ == '__main__':
    main()
