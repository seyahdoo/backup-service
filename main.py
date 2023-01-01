import rclone
from mail import send_mail_to_myself


def main():
    # send_mail_to_myself("ERROR on Backup Service", "Error")
    def handle_error_line(line):
        print(line)
    rclone.copy("C:/Users/kardan/Videos", "gdrive:Rsync/Beast/Videos", handle_error_line, handle_error_line)
    return


if __name__ == '__main__':
    main()
