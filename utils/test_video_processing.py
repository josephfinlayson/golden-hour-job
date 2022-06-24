from utils.video_processing import orchestrate_video_creation


def test_image_to_video():

    response = orchestrate_video_creation(['./fixtures/sample.jpg', './fixtures/sample_2.jpg'], "blah")
    print(response)
    assert type(response['file']) == str