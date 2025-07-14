import boto3


def verify_static_files(bucket_name, prefix="static/"):
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if "Contents" not in response or len(response["Contents"]) == 0:
        raise RuntimeError("❌ S3에 static 파일이 없습니다.")
    print(f"✅ static 파일 {len(response['Contents'])}개 확인됨.")


# 실행 예시
if __name__ == "__main__":
    verify_static_files("your-bucket-name")
