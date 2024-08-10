from linebot.models import FlexSendMessage, BubbleContainer, \
    BoxComponent, TextComponent, ButtonComponent, PostbackAction

def create_all_counter_message():
    events = [
        {'C': '主日', 'D': '禱告\n聚會', 'E': '家聚會'},
        {'F': '家受訪', 'G': '小排', 'H': '晨興'},
        {'I': '傳福音', 'J': '生命\n讀經'},
        {'K': '天天生\n命讀經', 'L': '個人\n禱告'}
    ]
    all_contents = []
    for box in events:
        contents = []
        for event_id, event in box.items():
            contents.append(
                ButtonComponent(
                    action=PostbackAction(
                        label=f'{event}',
                        data=f'event:{event_id}&attend:TRUE',
                        size='lg',
                        margin='xs'
                    ),
                    style='primary',
                    color='#FFA500'
                )
            )
        all_contents.append(
            BoxComponent(
                layout='horizontal',
                contents=contents,
                spacing='md',
            )
        )
    all_contents.insert(0, TextComponent(text='週點名', weight='bold', size='xl'))

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