import unittest, glob, os, scipy

import numpy as N

from neuroimaging.image.onesample import ImageOneSample
from neuroimaging.sandbox.refactoring.baseimage import image
from neuroimaging.tests.data import repository

class BaseImageTest(unittest.TestCase):

    def setUp(self):
        self.img = image("avg152T1.img", repository)
        self.rho = image("rho.img", datasource=repository)

    def tearDown(self):
        tmpf = glob.glob('tmp.*')
        for f in tmpf: os.remove(f)

    def test_analyze(self):
        y = self.img.array
        self.assertEquals(y.shape, tuple(self.img.grid.shape))
        y.shape = N.product(y.shape)
        self.assertEquals(N.maximum.reduce(y), 437336.375)
        self.assertEquals(N.minimum.reduce(y), 0.)

    def test_slice1(self):
        x = self.img[3]
        self.assertEquals(x.shape, tuple(self.img.grid.shape[1:]))
        
    def test_slice2(self):
        x = self.img[3:5]
        self.assertEquals(x.shape, (2,) + tuple(self.img.grid.shape[1:]))

    def test_slice3(self):
        s = slice(0,20,2)
        x = self.img[s]
        self.assertEquals(x.shape, (10,) + tuple(self.img.grid.shape[1:]))

    def test_slice4(self):
        x = self.img[:]
        self.assertEquals(x.shape, tuple((self.img.grid.shape)))

    def test_slice5(self):
        s1 = slice(0,20,2)
        s2 = slice(0,50,5)
        x = self.img[(s1,s2)]
        self.assertEquals(x.shape, (10,10,self.img.grid.shape[2]))

    def test_array(self):
        x = self.img.array
        
    def test_write(self):
        x = self.img.write('tmp.img')

    def test_nondiag(self):
        self.img.grid.mapping.transform[0,1] = 3.0
        self.img.write('tmp.img')#, usematfile=True)
        scipy.testing.assert_almost_equal(
            image('tmp.img').grid.mapping.transform,
            self.img.grid.mapping.transform)

    def test_clobber(self):
        x = self.img.write('tmp.img', clobber=True)
        a = image('tmp')
        A = a.array
        I = self.img.array
        z = N.add.reduce(((A-I)**2).flat)
        self.assertEquals(z, 0.)
        t = a.grid.mapping.transform
        b = self.img.grid.mapping.transform
        scipy.testing.assert_almost_equal(b, t)

    def test_iter(self):
        I = iter(self.img)
        for i in I:
            self.assertEquals(i.shape, (109,91))

    def test_parcels1(self):
        rho = self.rho
        parcelmap = (rho.array * 100).astype(N.int32)
        test = image(N.zeros(parcelmap.shape), grid=rho.grid)
        test.grid.itertype = 'parcel'
        test.grid.parcelmap = parcelmap
       
        v = 0
        for t in test:
            v += t.shape[0]
        self.assertEquals(v, N.product(test.grid.shape))

    def test_parcels2(self):
        rho = self.rho
        parcelmap = (rho.array * 100).astype(N.int32)
        test = image(N.zeros(parcelmap.shape), grid=rho.grid)

        test.grid.itertype = 'parcel'
        test.grid.parcelmap = parcelmap
        parcelmap.shape = N.product(parcelmap.shape)
       
        v = 0
        iter(test)
        while True:
            try:
                test.next(data=v)
                v += 1
            except StopIteration:
                break

    def test_parcels3(self):
        rho = self.rho
        parcelmap = (rho.array * 100).astype(N.int32)
        shape = parcelmap.shape
        parcelmap.shape = N.product(parcelmap.shape)
        parcelseq = N.unique(parcelmap)

        test = image(N.zeros(shape), grid=rho.grid)
        test.grid.itertype = 'parcel'
        test.grid.parcelmap = parcelmap
        test.grid.parcelseq = parcelseq

        v = 0

        for t in test:
            v += t.shape[0]
        self.assertEquals(v, N.product(test.grid.shape))

    def test_onesample1(self):
        im1 = image('FIAC/fiac3/fonc3/fsl/fmristat_run/contrasts/speaker/effect.img',
            repository)
        im2 = image('FIAC/fiac4/fonc3/fsl/fmristat_run/contrasts/speaker/effect.img',
            repository)
        im3 = image('FIAC/fiac5/fonc2/fsl/fmristat_run/contrasts/speaker/effect.img',
            repository)
        x = ImageOneSample([im1,im2,im3], clobber=True)
        x.fit()

if __name__ == '__main__': unittest.main()