from django.db import IntegrityError, transaction
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Video
# Create your tests here.

class TestHomePageMessage(TestCase):
    
    def test_app_title_msg_displayed(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Welcome to Exercise Videos!')
        


class TestAddVideos(TestCase):

    # Adding a video, added to DB and video_id created 

    def test_add_video(self):

        add_video_url = reverse('add_video')

        valid_video = {
            'title': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            'notes': 'yoga for neck and shoulders'
        }
        
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows new video 
        self.assertContains(response, 'yoga')
        # self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')

        # video count on page is correct 
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first() 

        self.assertEqual('yoga', video.title)
        # self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('yoga for neck and shoulders', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_ID)



        # add another video - both present? 

        valid_video_2 = {
            'title': 'full body workout',
            'url': 'https://www.youtube.com/watch?v=IFQmOZqvtWg',
            'notes': '30 minutes of aerobics'
        }
        
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video_2, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        # video count on page is correct 
        self.assertContains(response, '2 videos')

        # video list shows both new videos


        # video 1, 
        self.assertContains(response, 'yoga')
        # self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')

        # and video 2
        self.assertContains(response, 'full body workout')
        # self.assertContains(response, 'https://www.youtube.com/watch?v=IFQmOZqvtWg')
        self.assertContains(response, '30 minutes of aerobics')

        # database contains two videos 
        self.assertEqual(2, Video.objects.count())

        # both video present on page? Another way to check is to query for a video with all the expected data. 
        # the get method will raise a DoesNotExist error if a matching video is not found, and that will cause the test to fail

        video_1_in_db = Video.objects.get(title='yoga', url='https://www.youtube.com/watch?v=4vTJHUDB5ak', \
        notes='yoga for neck and shoulders', video_ID='4vTJHUDB5ak')
        
        video_2_in_db = Video.objects.get(title='full body workout', url='https://www.youtube.com/watch?v=IFQmOZqvtWg', \
        notes='30 minutes of aerobics', video_ID='IFQmOZqvtWg')


        # how about the correct videeos in the context?
        videos_in_context = list(response.context['videos'])   # the object in the response is from a database query, so it's a QuerySet object. Convert to a list

        expected_videos_in_context = [video_2_in_db, video_1_in_db]  # in this order, because they'll be sorted by name 
        self.assertEqual(expected_videos_in_context, videos_in_context)


    # Notes are optional
    def test_add_video_no_notes_video_added(self):
        
        add_video_url = reverse('add_video')

        valid_video = {
            'title': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            # no notes
        }
        
        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        # video list shows new video 
        self.assertContains(response, 'yoga')
        # self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak') # my code doesn't include this as embedded video already has a link
        
        # video count on page is correct 
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first() 

        self.assertEqual('yoga', video.title)
        # self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEquals('', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_ID)



    # Invalid videos not added

    def test_add_video_missing_fields(self):

        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'title': '',   # no name, should not be allowed 
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                'title': 'example',   
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },
            {
                'title': 'example',  
                # no URL 
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name
                # no URL
                'notes': 'yoga for neck and shoulders'
            },
            {
                'title': '',   # blank - not allowed 
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },

        ]

        
        for invalid_video in invalid_videos:

            # follow=True not necessary because if video not valid, will expect a simple response
            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed('video_collection/add_video.html')  # still on add page 
            self.assertEqual(0, Video.objects.count())  # no video added to database 
            messages = response.context['messages']    # get the messages
            message_texts = [ message.message for message in messages ]   # and the message texts
            self.assertIn('Invalid form, please try again.', message_texts)   # is this message one of the messages? 

            # And we can also check that message is displayed on the page 
            self.assertContains(response, 'Invalid form, please try again.')


    #  Duplicates not allowed

    def test_add_duplicate_video_not_added(self):

        # Since an integrity error is raised, the database has to be rolled back to the state before this 
        # action (here, adding a duplicate video) was attempted. This is a separate transaction so the 
        # database might be in a weird state and future queries in this method can fail with atomic transaction errors. 
        # the solution is to ensure the entire transation is in an atomic block so the attempted save and subsequent 
        # rollback are completely finished before more DB transactions - like the count query - are attempted.

        # Most of this is handled automatically in a view function, but we have to deal with it here. 

        with transaction.atomic():
            new_video = {
                'title': 'yoga',
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            }

            # Create a video with this data in the database
            # the ** syntax unpacks the dictonary and converts it into function arguments
            # https://python-reference.readthedocs.io/en/latest/docs/operators/dict_unpack.html
            # Video.objects.create(**new_video)
            # with the new_video dictionary above is equivalent to 
            # Video.objects.create(name='yoga', url='https://www.youtube.com/watch?v=4vTJHUDB5ak', notes='for neck and shoulders')
            Video.objects.create(**new_video)

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

        with transaction.atomic():
            # try to create it again    
            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('Video ID already exists.', message_texts)

            self.assertContains(response, 'Video ID already exists.')  # and message displayed on page 

        # still one video in the database 
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)


    def test_add_video_invalid_url_not_added(self):

        # what other invalid strings shouldn't be allowed? 

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            '',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]


        for invalid_url in invalid_video_urls:

            new_video = {
                'title': 'yoga',
                'url': invalid_url,
                'notes': 'yoga for neck and shoulders'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form 
            self.assertTemplateUsed('video_collection/add.html')

            # Messages set correctly?
            messages = response.context['messages']
            message_texts = [ message.message for message in messages ]
            self.assertIn('Invalid URL, must be a YouTube video.', message_texts)
            self.assertIn('Invalid URL, must be a YouTube video.', message_texts)

            # and messages displayed on page
            self.assertContains(response, 'Invalid URL, must be a YouTube video.')
            self.assertContains(response, 'Invalid URL, must be a YouTube video.')

            # no videos in the database 
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)
        

class TestVideoList(TestCase):

    # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(title='ABC', notes='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        v2 = Video.objects.create(title='nope', notes='example', url='https://www.youtube.com/watch?v=O6mr2Tyg8uc')
        v3 = Video.objects.create(title='abc', notes='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        v4 = Video.objects.create(title='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=l7Wgr1FIVUA')

        expected_video_order = [v1, v3, v4, v2]
        response = self.client.get(reverse('video_list'))
        
        videos_in_template = list(response.context['videos'])
        
        self.assertEqual(expected_video_order, videos_in_template)


    # No video message 

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, '0 videos')
        self.assertEquals(0, len(videos_in_template))


    # 1 video vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(title='XYZ', notes='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   # check this, because '1 videos' contains '1 video'


    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(title='ABC', notes='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        v2 = Video.objects.create(title='nope', notes='example', url='https://www.youtube.com/watch?v=O6mr2Tyg8uc')
        v3 = Video.objects.create(title='abc', notes='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        v4 = Video.objects.create(title='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=l7Wgr1FIVUA')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(title='ABC', notes='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        v2 = Video.objects.create(title='nope', notes='example', url='https://www.youtube.com/watch?v=O6mr2Tyg8uc')
        v3 = Video.objects.create(title='abc', notes='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        v4 = Video.objects.create(title='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=l7Wgr1FIVUA')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(title='ABC', notes='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        v2 = Video.objects.create(title='nope', notes='example', url='https://www.youtube.com/watch?v=O6mr2Tyg8uc')
        v3 = Video.objects.create(title='abc', notes='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        v4 = Video.objects.create(title='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=l7Wgr1FIVUA')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, '0 videos')
        

        
        
class TestVideoModel(TestCase):

    def test_create_id(self):
        video = Video.objects.create(title='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_ID)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(title='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_ID)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(title='example', url='https://www.youtube.com/watch?v=b1DfSigfi50')
        v2 = Video.objects.create(title='different example', notes='example', url='https://www.youtube.com/watch?v=O6mr2Tyg8uc')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)  # check contents of two lists/iterables but order doesn't matter.


    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/watch?v1234',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu'
            'https://minneapolis.edu?v=123456'
            ''
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(title='example', url=invalid_url, notes='example notes')

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)


    def duplicate_video_raises_integrity_error(self):
        Video.objects.create(title='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        with self.assertRaises(IntegrityError):
            Video.objects.create(title='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')


class TestVideoDetails(TestCase):
    
    def test_video_detail_if_exist(self):
        # Create a video
        video = Video.objects.create(title='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        
        # Get the video details
        response = self.client.get(reverse('video_detail', kwargs={'video_pk':video.pk}))
        
        # Check if the video details are displayed
        self.assertTemplateUsed('video_collection/video_detail.html')
        

        self.assertContains(response, video.title)
        self.assertContains(response, video.url)
        self.assertContains(response, video.notes)
        
    def test_video_detail_if_not_exist(self):
        # Get the video details
        response = self.client.get(reverse('video_detail', kwargs={'video_pk':123}))
        
        
    
        self.assertTemplateUsed('video_collection/video_detail.html')
        
        # Check that it is not found
        self.assertEqual(404, response.status_code)