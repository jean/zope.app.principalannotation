##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Principal Annotation Tests

$Id$
"""
from unittest import TestCase, TestLoader, TextTestRunner
from zope import component as capi
from zope.interface import implements
from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.principalannotation import PrincipalAnnotationUtility
from zope.app.principalannotation import AnnotationsForPrincipal
from zope.app.security.interfaces import IPrincipal
from zope.app.component.testing import PlacefulSetup
from zope.app.testing import ztapi, setup
from interfaces import IPrincipalAnnotationUtility

class Principal(object):

    implements(IPrincipal)

    def __init__(self, id):
        self.id = id


class PrincipalAnnotationTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        sm = self.buildFolders(site='/')

        self.util = PrincipalAnnotationUtility()
        capi.provideUtility(self.util, IPrincipalAnnotationUtility)

    def testGetSimple(self):
        prince = Principal('somebody')
        self.assert_(not self.util.hasAnnotations(prince))

        princeAnnotation = self.util.getAnnotations(prince)
        # Just getting doesn't actualy store. We don't want to store unless
        # we make a change.
        self.assert_(not self.util.hasAnnotations(prince))

        princeAnnotation['something'] = 'whatever'

        # But now we should have the annotation:
        self.assert_(self.util.hasAnnotations(prince))

    def testGetFromLayered(self):
        princeSomebody = Principal('somebody')
        sm1 = self.makeSite('folder1')
        subUtil = setup.addUtility(sm1, '', IPrincipalAnnotationUtility,
                                   PrincipalAnnotationUtility())

        parentAnnotation = self.util.getAnnotations(princeSomebody)

        # Just getting doesn't actualy store. We don't want to store unless
        # we make a change.
        self.assert_(not subUtil.hasAnnotations(princeSomebody))

        parentAnnotation['hair_color'] = 'blue'

        # But now we should have the annotation:
        self.assert_(self.util.hasAnnotations(princeSomebody))

        subAnnotation = subUtil.getAnnotations(princeSomebody)
        self.assertEquals(subAnnotation['hair_color'], 'blue')

        subAnnotation['foo'] = 'bar'

        self.assertEquals(parentAnnotation.get("foo"), None)


    def testAdapter(self):
        p = Principal('somebody')
        ztapi.provideAdapter(IPrincipal, IAnnotations,
                             AnnotationsForPrincipal(self.util))
        annotations = IAnnotations(p)
        annotations["test"] = "bar"
        annotations = IAnnotations(p)
        self.assertEquals(annotations["test"], "bar")


def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(PrincipalAnnotationTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
