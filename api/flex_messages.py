from linebot.models import FlexSendMessage, BubbleContainer, \
    BoxComponent, TextComponent, ButtonComponent, PostbackAction

def create_all_counter_message(event_name, events):
    
    all_contents = []
    flip_color = '#0f53bf'
    other_color = '#6200ad'
    color = ''
    for box in events:
        contents = []
        if color == flip_color:
            color = other_color
        else:
            color = flip_color
        for event_id, event in box.items():
            if color == flip_color:
                color = other_color
            else:
                color = flip_color
            contents.append(
                ButtonComponent(
                    action=PostbackAction(
                        label=f'{event}',
                        data=f'event:{event_id}&attend:TRUE',
                        display_text=f'{box[event_id]} 簽到',
                        size='lg',
                        margin='xs'
                    ),
                    style='primary',
                    color=color
                )
            )
        all_contents.append(
            BoxComponent(
                layout='horizontal',
                contents=contents,
                spacing='md',
            )
        )
    all_contents.insert(0, TextComponent(text=event_name, weight='bold', size='xl'))

    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='xl',
            contents=all_contents
        )
    )
    flex_message = FlexSendMessage(
        alt_text='恩典點名', contents=bubble
    )
    return flex_message

def create_event_flex_message(event, event_id):
    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='xl',
            contents=[
                TextComponent(text=event, weight='bold', size='xl'),
                ButtonComponent(
                    action=PostbackAction(
                        label='我來了！',
                        data=f'event:{event_id}&attend:TRUE',
                        # display_text='已簽到！',
                        size='lg'
                    ),
                    style='primary'
                ),
                ButtonComponent(
                    action=PostbackAction(
                        label='我下次再來～',
                        data=f'event:{event_id}&attend:FALSE',
                        # display_text='下次來～！',
                        size='lg'
                    ),
                    style='secondary'
                )
            ]
        )
    )
    flex_message = FlexSendMessage(
        alt_text='恩典點名', contents=bubble
    )
    return flex_message