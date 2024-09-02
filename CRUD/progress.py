from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import schemas, models

import logging

'''
    Progress of all students of selcted group on selected quest
'''


async def getProgress(  
    db: Session, 
    group_id: str,
    quest_id: str
    ) -> list[schemas.StudentProgress]:
    '''
    Progress for all students of selcted group on selected quest
    - returns List[StudentProgress] - agregated progress from StudentTasks      
    '''

    # === Fetching data 

    '''
    student_id
    student_full_name
    quest_start_at
    quest_end_at
    '''

    # in result we have array of len = students_count | timings for each student of group regarding chosen quest
    students_quest_times = db.query(
            models.StudentQuest.student_id,
            models.Student.full_name.label('student_full_name'),

            models.StudentQuest.start_at.label('quest_start_at'),
            models.StudentQuest.end_at.label('quest_end_at')
        )\
        .filter(
              models.StudentQuest.group_id == group_id,
              models.StudentQuest.quest_id == quest_id)\
        .join(
              models.Student, 
              models.StudentQuest.student_id == models.Student.id
              )\
        .order_by('student_id').all()  # comon sorting for both queries => sync

    '''
        tasks:
            task_name: str   # Task
            task_id: str     # StudentTask
            answer: bool     # StudentTask
            answered_at: str # StudentTask
    '''
    tasks = db.query(
        models.StudentTask.student_id,  # for task:student mapping bellow
        models.StudentTask.task_id,
        models.Task.name.label('task_name'),   # rename pole <=> "AS" in sql
        models.StudentTask.answer,
        models.StudentTask.answered_at  
        )\
     .filter(models.StudentTask.quest_id == quest_id)\
     .join(models.Task, models.StudentTask.task_id == models.Task.id)\
     .order_by('student_id', 'task_id').all() # common soring for both queries => sync


    # === Forming response

    # check if there`s nobody in group started selected quest
    if len(students_quest_times) == 0:
        return []

    '''
    - forming respnse data,
    - maintainig "count_`s",

    Remembering:
        - tasks` len >= students_quest_times` len = students len 
        - both tasks and students_quest_times - are ordered by student_id 
    Conclude: 
        - can syncronize traversing over tasks and students_quest_times - by index (stud_idx) in students_quest_times
    ''' 

    def final_counts(cur_student: schemas.StudentProgress):
        '''Upadate counts when all tasks of student is already traversed'''
        cur_student.quest_total_tasks_count = len(cur_student.tasks)
        cur_student.quest_false_answer_count = cur_student.quest_total_tasks_count - cur_student.quest_true_answer_count


    ''' Debug DB results:    
    for x in students_quest_times: print(f'+  {x}')
    for x in tasks: print(f'*  {x}')
    '''
    

    stud_idx = 0 # synchro index - processing student`s idx
    cur_student = schemas.StudentProgress(  # mini-initing 0-th el - to start cycle properly 
        **students_quest_times[0]._mapping, # mapping - dictionary repr
        quest_true_answer_count = 0,
        tasks=[]
        )
    group_progress = [cur_student]  # response array

    # grouping tasks by students and counting true_count, also synchronizing with students_quest_times when another student`s task are traversed  - else branch 
    for task in tasks:
        student_id = task.student_id
        task_dict = task._mapping   
        
        # update existing student progress: (task) => (+ tasks, ?+ true_count)
        if student_id == cur_student.student_id:
            cur_student.tasks.append(schemas.TaskView(**task_dict))
            if task.answer:
                cur_student.quest_true_answer_count += 1 
        
        # or init new student progress
        else:
            final_counts(cur_student) # update counts

            stud_idx += 1
            cur_student = schemas.StudentProgress(      # new student progress
                **students_quest_times[stud_idx]._mapping,       # alreafy known poles for such student
                tasks=[schemas.TaskView(**task_dict)],  # first task for newly added student progress
                quest_true_answer_count = 1 if task.answer else 0
                )
            group_progress.append(cur_student)
    

    # update counts for last student 
    final_counts(cur_student)

    return group_progress



# just reading all - no pagination, filtering and sorting (left to frontend)
async def read(
    db: Session, 
    group_id: str,
    quest_id: str
    ):

    progress = await getProgress(db, group_id=group_id, quest_id=quest_id)
    return schemas.API_Response(
        data = progress,
        meta = schemas.API_Response.MetaData(total=len(progress))
    )