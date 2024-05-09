Update_National_Manager_PROFILE = 'UPDATE manager SET title ="{}", firstName ="{}",familyName ="{}",position ="{}",phoneNumber ="{}" WHERE userId="{}"'

queryNationalManagerInfoByUserId= 'select username,email,password,role,title,firstName,familyName,position,phoneNumber from Managers as m,Users as u where u.id=m.userId and m.userId={}'