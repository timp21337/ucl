import os
from django.db import models, connection

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


from datetime import date

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '../')


def initialise():
    admin = User.objects.create_superuser('admin', 'adam@example.org', 'admin')
    admin.first_name = "Adam"
    admin.last_name = "Admin"
    admin.save()

class Member(User):

    gender = models.CharField(max_length=1,
                              choices=(('M', 'Male'), ('F', 'Female')),
                              default= 'F')
    address = models.TextField(blank=True)

    mobile = models.CharField(max_length=16, blank=True)
    landline = models.CharField(max_length=16, blank=True)

    dob = models.DateField(help_text='Format: YYYY-MM-DD',
                           validators=[MinValueValidator(date(1900, 7, 22)),
                                       MaxValueValidator(date(2012, 12, 12))],
                           null=True,
                           blank=True)
    role = models.CharField(max_length=10,
                            choices=(('Member', 'Member'),
                                     ('Carer', 'Carer'),
                                     ('Backup', 'Backup'),
                                     ('Doctor', 'Doctor'),
                                     ('Helper', 'Helper'),
                                     ('Leader', 'Leader'),
                                     ('Officer', 'Officer'),
                                     ),
                            default= 'Member')
    status = models.CharField(max_length=10,
                              choices=(('Elfin', 'Elfin'),
                                       ('Pioneer', 'Pioneer'),
                                       ('Woodchip', 'Woodchip'),
                                       ('Gone', 'Gone'),
                                       ('Waiting', 'Waiting'),
                                       ('Carer', 'Carer'),
                                       ('Doctor', 'Doctor'),
                                       ),
                              null=True,
                              blank=True)

    joined = models.DateField(help_text='Format: YYYY-MM-DD',
                                   validators=[MinValueValidator(date(2011, 7, 22)),
                                               MaxValueValidator(date(2016, 12, 12))],
                                   null=True,
                                   blank=True,
                                   default=date.today())

    spam = models.BooleanField(default=False)


    class Meta:
        ordering = ['username']

    def __unicode__(self):
        return "%s (%s)" % (self.first_name, self.last_name)

    def is_adult(self):
        if self.role in ['Carer',
                         'Backup',
                         'Doctor',
                         'Helper',
                         'Leader',
                         'Officer']:
            return True
        else:
            return False

    def age(self):
        return int((date.today() - self.dob).days/365.25)

    @classmethod
    def summary(cls, selection, *args):
        method = getattr(cls, selection)
        total = 0
        adults = 0
        kids = 0
        for m in method(args):
            total += 1
            if m.is_adult():
                adults += 1
                print ("%-12s %-12s %s %s %s %s" % (m.first_name,
                                                    m.last_name,
                                                    m.membership_expired_alert(),
                                                    m.membership_expiry,
                                                    m.crb_expired_alert(),
                                                    m.crb_expiry))
            else:
                kids += 1
                print ("%-12s %-12s %s" % (m.first_name,
                                                 m.last_name,
                                                 m.age()))
        print "Total: %d Adults: %d Children: %d" %(total, adults, kids)
        connection.close()


    @classmethod
    def emails(cls, selection, *args):
        method = getattr(cls, selection)
        total = 0
        adults = 0
        kids = 0
        emails = set()
        for m in method(args):
            total += 1
            print m
            if m.is_adult():
                adults += 1
                if m.email != '':
                    emails.add(m.email)
            else:
                kids += 1
                if m.carer is not None and m.carer.email != '' :
                    emails.add(m.carer.email)
                if m.carer_2 is not None and m.carer_2.email != '' :
                    emails.add(m.carer_2.email)
        print ", ".join(sorted([str(e).lower() for e in emails]))
        print "%s " % [e for e in emails]
        print "Total: %d Adults: %d Children: %d" %(total, adults, kids)
        connection.close()



    @classmethod
    def members_with_status(cls, status):
        return [o for o in cls.objects.all() if o.status == status]

    @classmethod
    def members_with_role(cls, role):
        return [o for o in cls.objects.all() if o.role == role]



def dottedDict(model, name, dict):
    for f in model._meta.fields:
        if type(f) in [models.fields.related.ForeignKey, models.fields.related.OneToOneField]:
            referred = getattr(model, f.name)
            if referred is not None:
                dottedDict(referred, '%s.%s' % (name, f.name), dict)
        else:
            dict['%s.%s' % (name, f.name)] = model.__dict__[f.name]
    try:
        extras = getattr(model, 'extras')
        print "Has one:%s = %s" % (extras, extras())
        for m in extras():
            dict['%s.%s' % (name, m.__name__)] = m()
    except StandardError:
        pass

    return dict


class Session(models.Model):
    name = models.CharField(max_length=40, default=str(date.today()))
    start_date = models.DateField(help_text='Format: YYYY-MM-DD',
                                  null=True,
                                  default=date.today())
    end_date = models.DateField(help_text='Format: YYYY-MM-DD',
                                null=True,
                                default=date.today())

    def __unicode__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=160)

    def __unicode__(self):
        return self.name


class Book(models.Model):
    asin = models.CharField(primary_key=True, max_length=30)
    isbn = models.CharField(max_length=30)
    title = models.CharField(max_length=160)
    description = models.TextField()
    author = models.ForeignKey(Author, null=False, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.title

class Collection(models.Model):
    member = models.ForeignKey(Member, null=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField()
    created = models.DateField(help_text='Format: YYYY-MM-DD',
                               validators=[MinValueValidator(date(2011, 7, 22)),
                                           MaxValueValidator(date(2016, 12, 12))],
                               default=date.today())
    def __unicode__(self):
        return self.title

class CollectionBook(models.Model):
    collection = models.ForeignKey(Collection, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=False, on_delete=models.CASCADE)


class Tag(models.Model):
    title = models.CharField(max_length=160)
    def __unicode__(self):
        return self.title

class TagBook(models.Model):
    tag = models.ForeignKey(Tag, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=False, on_delete=models.CASCADE)


class Review(models.Model):
    book = models.ForeignKey(Book, null=False, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, null=False, on_delete=models.CASCADE)
    asin = models.CharField(primary_key=True, max_length=30)
    title = models.CharField(max_length=160)
    created = models.DateField(help_text='Format: YYYY-MM-DD',
                               validators=[MinValueValidator(date(2011, 7, 22)),
                                           MaxValueValidator(date(2016, 12, 12))],
                               default=date.today())
    stars = models.IntegerField(default=0, validators=[MaxValueValidator(5)])
    description = models.TextField()


    def __unicode__(self):
        return self.title

