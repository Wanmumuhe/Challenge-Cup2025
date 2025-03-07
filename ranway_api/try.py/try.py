import time
from runwayml import RunwayML
api_key = "key_2abb16899fed306a9968575600ea74529e74b8891ec02b8f0fc1bc7d1d8e42f948573ed8ea034ad6c8a107da19d452ef18dd85161f6d824baed84ec5345438a8"

client = RunwayML(api_key=api_key)

# Create a new image-to-video task using the "gen3a_turbo" model
task = client.image_to_video.create(
  model='gen3a_turbo',
  # Point this at your own image file
  prompt_image='D:\\Study\\cup\\try.png',
  prompt_text='smile',
)
task_id = task.id

# Poll the task until it's complete
time.sleep(10)  # Wait for a second before polling
task = client.tasks.retrieve(task_id)
while task.status not in ['SUCCEEDED', 'FAILED']:
  time.sleep(10)  # Wait for ten seconds before polling
  task = client.tasks.retrieve(task_id)

print('Task complete:', task)