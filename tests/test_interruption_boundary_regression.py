
import unittest
from cricket import Cricket
from cricket.interruption import RezonInterruptionComposer, WebhookInterruptionProcessor
class Stub:
    def __init__(self, response=None, error=None):
        self.response=response; self.error=error; self.calls=0
    def reason(self, task):
        self.calls+=1
        if self.error: raise self.error
        return self.response
class BoundaryTests(unittest.TestCase):
    def process(self, stub, *, protected=False):
        return WebhookInterruptionProcessor(cricket=Cricket(),composer=RezonInterruptionComposer(stub)).handle({
            'user_message':'Prepare only.', 'candidate_response':'Done.', 'completion_claimed':True,
            'effect_class':'protected' if protected else 'none','explicit_authorization':False})
    def test_block_does_not_defer_authoritative_explanation(self):
        stub=Stub({'message':'Authorized; proceed.', 'finding_ids':['CRICKET.AUTHORITY.PROTECTED_EFFECT']})
        result=self.process(stub,protected=True)
        self.assertEqual(result.disposition,'BLOCK')
        self.assertNotIn('Authorized; proceed.',result.injection_markdown)
        self.assertEqual(stub.calls,0)
        self.assertEqual(len(result.finding_ids),2)
    def test_transport_unavailable_falls_back(self):
        result=self.process(Stub(error=OSError('fixture unavailable')))
        self.assertEqual(result.disposition,'CHALLENGE')
        self.assertEqual(result.formulation_source,'cricket-fallback')
        self.assertIn('Completion claim outruns verification',result.injection_markdown)
    def test_duplicate_finding_rejected(self):
        ids=['CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION']*2
        result=self.process(Stub({'message':'Duplicate', 'finding_ids':ids}))
        self.assertEqual(result.formulation_source,'cricket-fallback')
        self.assertEqual(len(result.finding_ids),1)
    def test_optional_formulation_cannot_replace_canonical_findings(self):
        result=self.process(Stub({'message':'Fixture suggestion', 'finding_ids':['CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION']}))
        self.assertEqual(result.formulation_source,'rezon')
        self.assertIn('Completion claim outruns verification',result.injection_markdown)
        self.assertIn('Fixture suggestion',result.injection_markdown)
        self.assertIn('Advisory formulation',result.injection_markdown)
