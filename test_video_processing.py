from video_processing import prepare_video

def test_image_to_video():
    f1 = open('./sample.jpg', 'rb') 
    f2 = open('./sample_2.jpg', 'rb') 
    f1.seek(0)
    f2.seek(0)

    response = prepare_video([f1, f2], "blah")
    print(response)
    assert type(response['file'])== str