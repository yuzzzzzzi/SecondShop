from django.db import models
from django.contrib.auth.models import User,BaseUserManager, AbstractBaseUser
from django.core.files.storage import FileSystemStorage
# Create your models here.

class ImageStorage(FileSystemStorage):
    from django.conf import settings
    
    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        #初始化
        super(ImageStorage, self).__init__(location, base_url)

    #重写 _save方法        
    def _save(self, name, content):
        import os, time, random
        #文件扩展名
        ext = os.path.splitext(name)[1]
        #文件目录
        d = os.path.dirname(name)
        #定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0,100)
        #重写合成文件名
        name = os.path.join(d, fn + ext)
        #调用父类方法
        return super(ImageStorage, self)._save(name, content)

class MyUserManager(BaseUserManager):
    def create_user(self, username, nickname, telephone, password=None):
        """
        Creates and saves a User with the given username, nickname, telephone and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username = username,
            nickname = nickname, 
            telephone = telephone,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, telephone, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            password=password,
            nickname = nickname, 
            telephone = telephone,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    # user = models.OneToOneField(User,on_delete=models.CASCADE)
    username = models.CharField(verbose_name='用户名',max_length=40, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    telephone = models.CharField(verbose_name='电话号码',max_length=11)
    avatar = models.ImageField(verbose_name='头像',upload_to='avatar/', storage=ImageStorage() ,default="avatar/default_avatar.png")
    address = models.CharField(verbose_name='地址',max_length=200,default='',blank=True)
    major = models.TextField(verbose_name='个人简介',default='', blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nickname','telephone']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
