from linebot.models import FlexSendMessage, BubbleContainer, \
    BoxComponent, TextComponent, ButtonComponent, PostbackAction

def create_all_counter_message(event_name, events):
    
    all_contents = []
    for box in events:
        contents = []
        for event_id, event in box.items():
            contents.append(
                ButtonComponent(
                    action=PostbackAction(
                        label=f'{event}',
                        data=f'event:{event_id}&attend:TRUE',
                        display_text=f'{box[event_id]} 簽到',
                        size='lg',
                        margin='xs',
                        padding='xs'
                    ),
                    style='primary',
                    color='#FFFFFF'
                )
            )
        all_contents.append(
            BoxComponent(
                layout='horizontal',
                contents=contents,
                spacing='md',
            )
        )
    all_contents.insert(0, TextComponent(text=event_name, weight='bold', size='lg'))

    bubble = BubbleContainer(
        direction='ltr',
        body=BoxComponent(
            layout='vertical',
            spacing='xl',
            contents=all_contents
        )
    )
    flex_message = FlexSendMessage(
        alt_text=event_name, contents=bubble
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