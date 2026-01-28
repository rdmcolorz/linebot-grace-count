from linebot.models import FlexSendMessage, BubbleContainer, \
    BoxComponent, TextComponent, ButtonComponent, PostbackAction

def create_all_counter_message(event_name, event_data, state, related_names=None, selected_related=None, self_name=None):
    all_contents = [TextComponent(text=event_name, weight='bold', size='lg')]
    selected_related = selected_related or []
    rels_str = ",".join(selected_related) if selected_related else ""

    for box in event_data:
        contents = []
        for event_id, event in box.items():
            if event_id in state:
                style='primary'
            else:
                style='secondary'
            contents.append(
                ButtonComponent(
                    action=PostbackAction(
                        label=f'{event}',
                        data=f'action:n&state:{state + event_id}&rels:{rels_str}',
                        display_text=f'{event} 簽到',
                        flex=len(event),
                        margin='xs',
                        padding='xs',
                    ),
                    style=style,
                    adjust_mode='shrink-to-fit',
                    scaling=True
                    # color='#FFFFFF',
                    # border_color='#000000'
                )
            )
        all_contents.append(
            BoxComponent(
                layout='horizontal',
                contents=contents,
                spacing='md',
            )
        )
    # Related members quick actions (toggle selection)
    if related_names is not None or self_name is not None:
        participants = []
        if self_name:
            participants.append(self_name)
        if related_names:
            participants.extend(related_names)
        rel_buttons = []
        for name in participants:
            is_selected = name in selected_related
            rel_buttons.append(
                ButtonComponent(
                    action=PostbackAction(
                        label=name,
                        data=f'action:s&state:{state}&rels:{rels_str}&target:{name}',
                        display_text=f'選擇 {name}'
                    ),
                    style='primary' if is_selected else 'secondary',
                    color='#00C300' if is_selected else None,
                    adjust_mode='shrink-to-fit',
                    scaling=True
                )
            )
        all_contents.append(
            TextComponent(text='相關成員', size='sm', color='#888888')
        )
        all_contents.append(
            BoxComponent(
                layout='horizontal',
                contents=rel_buttons,
                spacing='md'
            )
        )
    all_contents.append(
        ButtonComponent(
            action=PostbackAction(
                label='確認送出',
                data=f'action:r&state:{state}&rels:{rels_str}',
                display_text='送出紀錄',
                size='lg',
                margin='xs',
                padding='xs',
            ),
            style='primary',
            adjust_mode='shrink-to-fit',
            scaling=True
        )
    )
    all_contents.append(
        ButtonComponent(
            action=PostbackAction(
                label='重新開始',
                data='action:n&state:&rels:',
                display_text='重新開始',
                size='lg',
                margin='xs',
                padding='xs',
            ),
            style='secondary',
            adjust_mode='shrink-to-fit',
            scaling=True
        )
    )

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