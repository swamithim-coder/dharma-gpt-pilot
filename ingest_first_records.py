from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

oa_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

collection_name = "dharma_qa_seed_en"

from qdrant_client.http.models import Distance, VectorParams

qdrant.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

records = [
    {"id": 1, "question": "What is Dharma?", "answer": "Dharma is righteous conduct that upholds life, society, and spiritual order.", "evidence": "Manusmriti 1.108 (paraphrased): Dharma sustains and upholds the order of life and society."},

    {"id": 2, "question": "What is Moksha?", "answer": "Moksha is liberation from the cycle of birth and death and the realization of the true Self.", "evidence": "Bhagavad Gita 2.51: The wise, freed from the cycle of birth and death, attain the highest state."},

    {"id": 3, "question": "What is Upanayanam?", "answer": "Upanayanam is the sacred-thread initiation into Vedic learning and discipline."},
     
    {"id": 5, "question": "What is Karma?", "answer": "Karma is action and the universal law by which every action, thought, and intention produces corresponding results according to Dharma.", "evidence": "Bhagavad Gita 4.17: 'Gahana karmano gatih' — the nature of action is profound and leads to consequences."},
  
    {"id": 18, "question": "What is truth (Satya)?", "answer": "Truth or Satya is the commitment to what is real and right, expressed through honesty and integrity.", "evidence": "Mahabharata: 'Satyam eva jayate' — Truth alone triumphs."},
     
    {"id": 19, "question": "What is non-violence (Ahimsa)?", "answer": "Ahimsa is the principle of non-violence, avoiding harm in thought, word, and action.", "evidence": "Mahabharata: 'Ahimsa paramo dharmah' — Non-violence is the highest Dharma."},

    

    {"id": 201, "question": "What is Karma?", "answer": "Karma is action and the universal law by which every action, thought, and intention produces corresponding results according to Dharma.", "evidence": "Bhagavad Gita 4.17: 'Gahana karmano gatih' — the nature of action is profound and leads to consequences."},
    {"id": 202, "question": "What is Bhakti Yoga?", "answer": "Bhakti Yoga is the path of devotion and loving surrender to the Lord through prayer, remembrance, and worship."},
    {"id": 203, "question": "What is Jnana Yoga?", "answer": "Jnana Yoga is the path of knowledge and self-inquiry leading to the realization of the true Self."},
    {"id": 204, "question": "What is Dhyana Yoga?", "answer": "Dhyana Yoga is the discipline of meditation that helps steady the mind and direct it toward the Self or the Divine."},
    {"id": 205, "question": "What is Nishkama Karma?", "answer": "Nishkama Karma means performing action without desire for personal gain or attachment to the result."},
    {"id": 206, "question": "What is Karma Phala?", "answer": "Karma Phala refers to the fruits or consequences that arise from one’s actions."},
    {"id": 207, "question": "What is Svadharma?", "answer": "Svadharma is one’s own duty based on role, stage of life, and righteous responsibility."},
    {"id": 208, "question": "What is Samatvam?", "answer": "Samatvam means equanimity, the balanced state of mind in success and failure, pleasure and pain."},
    {"id": 209, "question": "What is Saranagathi?", "answer": "Saranagathi is complete surrender and refuge in the Lord with faith and humility."},
    {"id": 210, "question": "What is Bhakti?", "answer": "Bhakti is devotion, love, and remembrance of the Divine with surrender and trust."},
    {"id": 211, "question": "What is Viveka?", "answer": "Viveka is discrimination between the eternal and the temporary, the real and the unreal."},
    {"id": 212, "question": "What is Vairagya?", "answer": "Vairagya is detachment from worldly cravings and desires while fulfilling one’s duties."},
    {"id": 213, "question": "What is Atman?", "answer": "Atman is the true Self, eternal and beyond the body and mind."},
    {"id": 214, "question": "What is Brahman?", "answer": "Brahman is the supreme absolute reality, infinite and eternal."},
    {"id": 215, "question": "What is Moksha?", "answer": "Moksha is liberation from the cycle of birth and death and the realization of the true Self.", "evidence": "Bhagavad Gita 2.51: The wise, freed from the cycle of birth and death, attain the highest state."},
    {"id": 216, "question": "What is Sattva?", "answer": "Sattva is the quality of purity, clarity, harmony, and knowledge."},
    {"id": 217, "question": "What is Rajas?", "answer": "Rajas is the quality of activity, desire, restlessness, and passion."},
    {"id": 218, "question": "What is Tamas?", "answer": "Tamas is the quality of inertia, ignorance, laziness, and delusion."},
    {"id": 219, "question": "What is Moha?", "answer": "Moha is delusion or attachment that clouds right judgment."},
    {"id": 220, "question": "What is Krodha?", "answer": "Krodha means anger arising from frustration, attachment, or obstruction of desire."},
    {"id": 221, "question": "What is Lobha?", "answer": "Lobha means greed or excessive desire for possession and gain."},
    {"id": 222, "question": "What is Shraddha?", "answer": "Shraddha is faith, trust, and reverence toward truth, scripture, and the Divine."},
    {"id": 223, "question": "What is Seva?", "answer": "Seva is selfless service offered without expectation of reward."},
    {"id": 224, "question": "What is Tyaga?", "answer": "Tyaga means renunciation of attachment and ego in action."},
    {"id": 225, "question": "What is Prasada Buddhi?", "answer": "Prasada Buddhi is the attitude of accepting all results as the grace of the Lord."},
    {"id": 226, "question": "How to handle stress through Karma Yoga?", "answer": "Handle stress by focusing on performing your duty sincerely without attachment to the result. Offer the action and outcome to the Lord."},
    {"id": 227, "question": "How to overcome anger?", "answer": "Anger can be reduced by self-awareness, patience, controlled speech, and reflecting before reacting."},
    {"id": 228, "question": "How to reduce anxiety about results?", "answer": "Reduce anxiety by concentrating on right effort and accepting results with Prasada Buddhi."},
    {"id": 229, "question": "How to deal with failure?", "answer": "View failure as an opportunity for learning and continue righteous effort without losing balance."},
    {"id": 230, "question": "How to face loss?", "answer": "Face loss with acceptance, prayer, and understanding that all worldly things are temporary."},
    {"id": 231, "question": "How to handle grief?", "answer": "Grief should be handled with prayer, reflection, support from family, and remembrance of the eternal Self."},
    {"id": 232, "question": "How to control the mind?", "answer": "The mind is controlled through discipline, meditation, prayer, and repeated practice."},
    {"id": 233, "question": "How to reduce greed?", "answer": "Reduce greed through contentment, charity, and reflection on impermanence."},
    {"id": 234, "question": "How to practice equanimity?", "answer": "Practice equanimity by remaining balanced in success and failure."},
    {"id": 235, "question": "How to develop devotion?", "answer": "Devotion grows through daily prayer, chanting, remembrance, and surrender to the Divine."},
    {"id": 236, "question": "How to surrender to the Lord?", "answer": "Surrender means offering your fears, desires, and actions to the Lord with trust."},
    {"id": 237, "question": "How to deal with jealousy?", "answer": "Jealousy can be reduced through gratitude and focus on self-improvement."},
    {"id": 238, "question": "How to stay disciplined?", "answer": "Discipline grows through routine, commitment, and control over the senses."},
    {"id": 239, "question": "How to handle family conflict?", "answer": "Family conflict should be approached with patience, truthfulness, and compassion."},
    {"id": 240, "question": "How to balance work and Dharma?", "answer": "Balance work and Dharma by performing professional duties ethically and maintaining daily spiritual discipline."},
    {"id": 241, "question": "How to practice prayer daily?", "answer": "Set aside fixed morning and evening time for prayer and reflection."},
    {"id": 242, "question": "How to improve concentration?", "answer": "Concentration improves through meditation, reduced distractions, and focused effort."},
    {"id": 243, "question": "How to reduce ego?", "answer": "Ego reduces through humility, service, and remembrance that all ability is Divine grace."},
    {"id": 244, "question": "How to remain humble?", "answer": "Humility is maintained through gratitude, service, and respect for others."},
    {"id": 245, "question": "How to live ethically?", "answer": "Live ethically through truthfulness, non-harm, discipline, and fairness."},
    {"id": 246, "question": "How to practice compassion?", "answer": "Compassion is practiced by helping others selflessly and speaking kindly."},
    {"id": 247, "question": "How to control speech?", "answer": "Speech should be truthful, kind, and measured."},
    {"id": 248, "question": "How to develop patience?", "answer": "Patience develops through tolerance, faith, and steady practice."},
    {"id": 249, "question": "How to cultivate inner peace?", "answer": "Inner peace arises from prayer, meditation, detachment, and acceptance."},
    {"id": 250, "question": "How to remain truthful?", "answer": "Truthfulness means aligning thought, word, and action with Dharma."}, 
    {"id": 251, "question": "What is student dharma?", "answer": "Student dharma is disciplined learning, respect for teachers, self-control, and dedication to knowledge and character."},
    {"id": 252, "question": "What is householder dharma?", "answer": "Householder dharma is the righteous fulfillment of duties toward family, society, work, and spiritual life."},
    {"id": 253, "question": "What is husband dharma?", "answer": "Husband dharma includes responsibility, protection, respect, support, and truthful conduct toward the family."},
    {"id": 254, "question": "What is wife dharma?", "answer": "Wife dharma includes care, support, respect, harmony, and righteous partnership in family life."},
    {"id": 255, "question": "What is parent dharma?", "answer": "Parent dharma is nurturing, guiding, protecting, and raising children with values and discipline."},
    {"id": 256, "question": "What is employee dharma?", "answer": "Employee dharma is sincerity, honesty, discipline, respect, and ethical performance of one’s work."},
    {"id": 257, "question": "What is employer dharma?", "answer": "Employer dharma is fairness, compassion, justice, and responsible leadership toward employees."},
    {"id": 258, "question": "What is business dharma?", "answer": "Business dharma is ethical trade, fairness, honesty, and responsibility toward customers and society."},
    {"id": 259, "question": "What is teacher dharma?", "answer": "Teacher dharma is imparting knowledge truthfully, patiently, and with compassion."},
    {"id": 260, "question": "What is priest dharma?", "answer": "Priest dharma is performing rituals correctly, preserving tradition, and guiding devotees spiritually."},
    {"id": 261, "question": "What is ruler dharma?", "answer": "Ruler dharma is just governance, protection of people, and upholding righteousness."},
    {"id": 262, "question": "What is social worker dharma?", "answer": "Social worker dharma is selfless service to society and upliftment of the needy."},
    {"id": 263, "question": "What is soldier dharma?", "answer": "Soldier dharma is courage, discipline, loyalty, and protection of the nation and people."},
    {"id": 264, "question": "What is police dharma?", "answer": "Police dharma is maintaining law, order, justice, and protection of society."},
    {"id": 265, "question": "What is doctor dharma?", "answer": "Doctor dharma is compassionate care, preservation of life, and ethical medical practice."},
    {"id": 266, "question": "What is lawyer dharma?", "answer": "Lawyer dharma is defending justice, truth, and fairness within the law."},
    {"id": 267, "question": "What is judge dharma?", "answer": "Judge dharma is impartial judgment, fairness, and protection of justice."},
    {"id": 268, "question": "What is administrator dharma?", "answer": "Administrator dharma is responsible governance, fairness, and efficient service."},
    {"id": 269, "question": "What is elder dharma?", "answer": "Elder dharma is guidance, wisdom, and support for younger generations."},
    {"id": 270, "question": "What is retiree dharma?", "answer": "Retiree dharma is spiritual reflection, guidance to family, and service to society."},
    {"id": 271, "question": "How should a student live?", "answer": "A student should live with discipline, humility, focused study, and respect for teachers and parents."},
    {"id": 272, "question": "How should a householder live?", "answer": "A householder should live responsibly, ethically, and with balance between family duties and spiritual discipline."},
    {"id": 273, "question": "How should a leader act?", "answer": "A leader should act with integrity, courage, compassion, and justice."},
    {"id": 274, "question": "How should a professional act ethically?", "answer": "A professional should act with honesty, competence, fairness, and accountability."},
    {"id": 275, "question": "How should a devotee live?", "answer": "A devotee should live with devotion, humility, prayer, service, and surrender to the Divine."},
    {"id": 276, "question": "What is duty to parents?", "answer": "Duty to parents is respect, care, gratitude, support, and service throughout life."},
    {"id": 277, "question": "What is duty to children?", "answer": "Duty to children is nurturing, education, guidance, protection, and moral upbringing."},
    {"id": 278, "question": "What is duty to society?", "answer": "Duty to society is ethical conduct, compassion, service, and contribution to collective welfare."},
    {"id": 279, "question": "What is duty to nation?", "answer": "Duty to nation is lawful conduct, service, responsibility, and protection of public good."},
    {"id": 280, "question": "What is duty to the environment?", "answer": "Duty to the environment is preserving nature, avoiding harm, and living responsibly."},
    {"id": 281, "question": "What is charity dharma?", "answer": "Charity dharma is selfless giving to support the needy and uphold righteousness."},
    {"id": 282, "question": "What is dana?", "answer": "Dana means charitable giving with humility and without expectation of return."}, 
    {"id": 283, "question": "What is anna dana?", "answer": "Anna dana is the offering of food to those in need and is considered highly meritorious."},
    {"id": 284, "question": "What is seva to society?", "answer": "Seva to society is selfless service for the welfare of others."},
    {"id": 285, "question": "What is temple dharma?", "answer": "Temple dharma includes reverence, purity, discipline, worship, and service in sacred spaces."},
    {"id": 286, "question": "What is brahmacharya dharma?", "answer": "Brahmacharya dharma is disciplined learning, celibacy, self-control, and focus on knowledge."},
    {"id": 287, "question": "What is grihastha dharma?", "answer": "Grihastha dharma is fulfilling family, social, and professional duties while living ethically."},
    {"id": 288, "question": "What is vanaprastha dharma?", "answer": "Vanaprastha dharma is gradual withdrawal from worldly duties and increased spiritual reflection."},
    {"id": 289, "question": "What is sannyasa dharma?", "answer": "Sannyasa dharma is renunciation, detachment, and complete dedication to spiritual realization."},
    {"id": 290, "question": "What is morning spiritual routine?", "answer": "A morning spiritual routine includes prayer, meditation, gratitude, and setting righteous intention for the day."},
    {"id": 291, "question": "What is evening prayer discipline?", "answer": "Evening prayer discipline includes reflection, gratitude, prayer, and mental calm before rest."},
    {"id": 292, "question": "What is ancestor duty?", "answer": "Ancestor duty includes remembrance, gratitude, and prescribed rites for forefathers."},
    {"id": 293, "question": "What is respect for guru?", "answer": "Respect for guru means humility, service, obedience, and gratitude toward the teacher."},
    {"id": 294, "question": "What is respect for elders?", "answer": "Respect for elders includes reverence, listening, service, and gratitude for their guidance."},
    {"id": 295, "question": "What is duty in crisis?", "answer": "Duty in crisis is to remain calm, act ethically, protect others, and uphold Dharma."},
    {"id": 296, "question": "What is Dharma?", "answer": "Dharma is righteous conduct that upholds life, society, and spiritual order.", "evidence": "Manusmriti 1.108 (paraphrased): Dharma sustains and upholds the order of life and society."},
    {"id": 297, "question": "What is dharma in workplace stress?", "answer": "Dharma in workplace stress is balanced effort, ethical conduct, patience, and detachment from results."},
    {"id": 298, "question": "What is dharma in financial hardship?", "answer": "Dharma in financial hardship is honest effort, discipline, contentment, and faith."},
    {"id": 299, "question": "What is dharma in illness?", "answer": "Dharma in illness is patience, self-care, prayer, and trust in treatment and Divine grace."},
    {"id": 300, "question": "What is dharma in grief?", "answer": "Dharma in grief is acceptance, remembrance of the eternal Self, and support from loved ones."},
    {"id": 301, "question": "What is Karma?", "answer": "Karma is action and the universal law by which every action, thought, and intention produces corresponding results according to Dharma.", "evidence": "Bhagavad Gita 4.17: 'Gahana karmano gatih' — the nature of action is profound and leads to consequences."},
    {"id": 302, "question": "What is Sanatana Dharma?", "answer": "Sanatana Dharma is the timeless, beginningless way of life rooted in the Vedas. It is understood as the eternal order aligned with truth, righteousness, and the natural law that sustains life and spiritual progress."},

    {"id": 303, "question": "Why do religions exist?", "answer": "Religions exist to guide people away from selfish living, establish righteous conduct, and lead them toward God, inner discipline, and lasting well-being beyond temporary pleasures."},

    {"id": 304, "question": "What is Karma?", "answer": "Karma is action and the universal law by which every action, thought, and intention produces corresponding results according to Dharma.", "evidence": "Bhagavad Gita 4.17: 'Gahana karmano gatih' — the nature of action is profound and leads to consequences."},
    {"id": 401, "question": "Why should one follow Dharma?", "answer": "One should follow Dharma because Dharma protects the individual and society, disciplines life, and leads one toward higher good and spiritual well-being."},
    {"id": 402, "question": "What is Moksha?", "answer": "Moksha is liberation from the cycle of birth and death and the realization of the true Self in union with the highest reality."},

    {"id": 403, "question": "Why do human beings suffer?", "answer": "Human beings suffer because of ignorance, attachment, desire, and the consequences of karma, which bind them to sorrow and repeated dissatisfaction."},

    {"id": 404, "question": "Why is desire considered dangerous?", "answer": "Desire is considered dangerous because it creates attachment, disturbs the mind, leads to frustration and anger, and keeps a person bound to suffering."},

   {"id": 405, "question": "What is Aachara?", "answer": "Aachara is prescribed righteous conduct in daily life, including discipline, purity, and adherence to Dharma in thought, word, and action."},

    {"id": 406, "question": "What is Svadharma?", "answer": "Svadharma is one’s own duty according to one’s nature, role, stage of life, and righteous responsibility."},

   {"id": 407, "question": "What is Karma Yoga?", "answer": "Karma Yoga is the path of selfless action in which one performs duty without attachment to the fruits and offers actions in a spirit of Dharma and devotion."},

   {"id": 408, "question": "What is Jnana Yoga?", "answer": "Jnana Yoga is the path of knowledge and discrimination through which one realizes the true Self and the nature of ultimate reality."},

   {"id": 409, "question": "What is Bhakti?", "answer": "Bhakti is loving devotion to the Divine expressed through faith, surrender, remembrance, worship, and heartfelt dedication."},

   {"id": 410, "question": "What is duty to parents?", "answer": "Duty to parents is to honor, respect, care for, support, and serve them with gratitude as an important part of Dharma."},

   {"id": 411, "question": "What is duty to children?", "answer": "Duty to children is to nurture, protect, educate, guide, and raise them in values, discipline, and righteous living according to Dharma."},
   {"id": 412, "question": "What is Dharma?", "answer": "Dharma is righteous conduct that upholds life, society, and spiritual order.", "evidence": "Manusmriti 1.108 (paraphrased): Dharma sustains and upholds the order of life and society."},

   {"id": 413, "question": "What is Adharma?", "answer": "Adharma is conduct that goes against righteousness, truth, and moral order, leading to disorder, suffering, and spiritual decline."},

   {"id": 414, "question": "What is righteous living?", "answer": "Righteous living is living in accordance with Dharma through right thought, right action, truthfulness, and moral discipline."},

   {"id": 415, "question": "What is purity in Dharma?", "answer": "Purity in Dharma refers to cleanliness and discipline of body, mind, and actions, maintaining sincerity, clarity, and moral integrity."},

   {"id": 416, "question": "What is discipline in life?", "answer": "Discipline in life is the consistent practice of self-control, order, and adherence to Dharma in daily conduct."},

   {"id": 417, "question": "What is self-control?", "answer": "Self-control is the ability to regulate one's thoughts, desires, and actions in alignment with Dharma and higher purpose."},

   {"id": 418, "question": "What is truth (Satya)?", "answer": "Truth or Satya is the commitment to what is real and right, expressed through honesty and integrity.", "evidence": "Mahabharata: 'Satyam eva jayate' — Truth alone triumphs."},

   {"id": 419, "question": "What is non-violence (Ahimsa)?", "answer": "Ahimsa is the principle of non-violence, avoiding harm in thought, word, and action.", "evidence": "Mahabharata: 'Ahimsa paramo dharmah' — Non-violence is the highest Dharma."},

   {"id": 420, "question": "What is compassion?", "answer": "Compassion is the quality of understanding the suffering of others and responding with kindness, care, and a desire to help."},
 
  {"id": 421, "question": "What is forgiveness?", "answer": "Forgiveness is the ability to let go of resentment and anger, and to respond with understanding and inner peace."},

   {"id": 422, "question": "What is the goal of human life according to Dharma?", "answer": "The goal of human life according to Dharma is to realize the true Self, live righteously, and ultimately attain liberation (Moksha)."},

   {"id": 423, "question": "What are the four Purusharthas?", "answer": "The four Purusharthas are Dharma (righteousness), Artha (wealth), Kama (desire), and Moksha (liberation), which together guide a balanced human life."},

  {"id": 424, "question": "What is Artha?", "answer": "Artha is the pursuit of material well-being, wealth, and security, guided by Dharma and used responsibly."},

  {"id": 425, "question": "What is Kama?", "answer": "Kama is the pursuit of desire, enjoyment, and emotional fulfillment, to be guided and regulated by Dharma."},

  {"id": 426, "question": "Why must Artha and Kama be guided by Dharma?", "answer": "Artha and Kama must be guided by Dharma to ensure that wealth and desires do not lead to harm, excess, or unrighteous living."},

  {"id": 427, "question": "What is the importance of Dharma in daily life?", "answer": "Dharma provides guidance for right conduct, discipline, and harmony in daily life, helping individuals live with purpose and integrity."},

  {"id": 428, "question": "What is inner purity?", "answer": "Inner purity is the state of a clear and disciplined mind free from negative thoughts, attachments, and impurities."},

  {"id": 429, "question": "What is outer purity?", "answer": "Outer purity refers to cleanliness and proper conduct in physical actions, surroundings, and daily practices."},

  {"id": 430, "question": "What is contentment?", "answer": "Contentment is the state of being satisfied with what one has, while maintaining peace of mind and freedom from excessive desire."},

  {"id": 431, "question": "What is greed?", "answer": "Greed is excessive desire for more than what is needed, leading to imbalance, dissatisfaction, and deviation from Dharma."},  

  {"id": 432, "question": "What is duty to society?", "answer": "Duty to society is to contribute to collective well-being through honest work, respect for others, and adherence to Dharma in social conduct."},

  {"id": 433, "question": "What is charity (Dana)?", "answer": "Dana is the act of giving selflessly to those in need, performed with humility and without expectation of return."},

  {"id": 434, "question": "Why is charity important in Dharma?", "answer": "Charity is important because it reduces selfishness, supports those in need, and promotes compassion and social harmony."},

  {"id": 435, "question": "Why is charity important in Dharma?", "answer": "Seva is selfless service performed for the benefit of others without desire for personal gain."},

  {"id": 436, "question": "What is respect for elders?", "answer": "Respect for elders is honoring, listening to, and caring for those who are older with humility and gratitude."},

  {"id": 437, "question": "What is humility?", "answer": "Humility is the quality of being free from arrogance, recognizing one's limitations, and remaining grounded in Dharma."},

  {"id": 438, "question": "What is patience?", "answer": "Patience is the ability to remain calm and steady in difficult situations without anger or frustration."},

  {"id": 439, "question": "What is anger and why should it be controlled?", "answer": "Anger is an intense emotional reaction that can lead to harmful actions, and it should be controlled to maintain peace, clarity, and righteous conduct."},

  {"id": 440, "question": "What is attachment?", "answer": "Attachment is excessive emotional dependence on people or objects, which leads to suffering when expectations are not met."},

  {"id": 441, "question": "What is detachment?", "answer": "Detachment is the ability to remain inwardly free and balanced, without excessive attachment to outcomes or possessions."},

  {"id": 442, "question": "What is equanimity?", "answer": "Equanimity is the state of mental balance and calmness in both success and failure, pleasure and pain."},

  {"id": 443, "question": "What is spiritual discipline?", "answer": "Spiritual discipline is the regular practice of self-control, study, reflection, and devotion to progress on the spiritual path."},

  {"id": 444, "question": "What is meditation?", "answer": "Meditation is the practice of focusing the mind inward to achieve clarity, peace, and awareness of the true Self."},

  {"id": 445, "question": "What is prayer?", "answer": "Prayer is the act of connecting with the Divine through devotion, gratitude, and sincere intention."},

  {"id": 446, "question": "What is surrender to God?", "answer": "Surrender to God is the attitude of offering one's actions, results, and life to the Divine with trust and devotion."},

  {"id": 447, "question": "What is devotion in daily life?", "answer": "Devotion in daily life is remembering the Divine through prayer, gratitude, righteous conduct, and sincere dedication in one's daily actions."},

  {"id": 448, "question": "Why is daily prayer important?", "answer": "Daily prayer is important because it purifies the mind, strengthens devotion, and keeps one connected to the Divine and to Dharma."},

  {"id": 449, "question": "What is gratitude?", "answer": "Gratitude is the recognition of blessings received from God, parents, teachers, and society, expressed through humility and thankfulness."},

  {"id": 450, "question": "Why should one practice self-control?", "answer": "One should practice self-control because it protects the mind from excess desire and anger, strengthens character, and supports righteous living."},

  {"id": 451, "question": "What is righteous conduct?", "answer": "Righteous conduct is behavior aligned with truth, self-discipline, compassion, and Dharma in thought, word, and action."},

  {"id": 452, "question": "Why is spiritual reflection important?", "answer": "Spiritual reflection is important because it helps a person examine life, correct mistakes, deepen wisdom, and move closer to the true purpose of life."},
  
  {"id": 453, "question": "What are the four Ashramas?", "answer": "The four Ashramas are Brahmacharya, Grihastha, Vanaprastha, and Sannyasa, which represent the stages of life in Dharma."},

{"id": 454, "question": "What is Brahmacharya?", "answer": "Brahmacharya is the stage of disciplined student life focused on learning, self-control, and character development."},

{"id": 455, "question": "What is Grihastha Ashrama?", "answer": "Grihastha Ashrama is the stage of household life where one fulfills duties to family, society, and sustains Dharma through responsible living."},

{"id": 456, "question": "What is Vanaprastha?", "answer": "Vanaprastha is the stage of gradual withdrawal from worldly responsibilities, focusing more on spiritual practices and detachment."},

{"id": 457, "question": "What is Sannyasa?", "answer": "Sannyasa is the stage of renunciation where one gives up worldly attachments and dedicates life entirely to spiritual realization."},

{"id": 458, "question": "What is the role of a householder?", "answer": "The role of a householder is to support family, contribute to society, practice charity, and uphold Dharma through responsible living."},

{"id": 459, "question": "Why is family life important in Dharma?", "answer": "Family life is important because it sustains society, provides a foundation for values, and supports the practice of Dharma."},

{"id": 460, "question": "What is control of mind?", "answer": "Control of mind is the ability to regulate thoughts, emotions, and desires through discipline and awareness."},

{"id": 461, "question": "How to control anger?", "answer": "Anger can be controlled through self-awareness, patience, reflection, and practicing restraint and calmness."},

{"id": 462, "question": "How to reduce desire?", "answer": "Desire can be reduced by practicing contentment, self-discipline, detachment, and focusing on higher goals."},

{"id": 463, "question": "What is Ishvara?", "answer": "Ishvara is the Supreme Being or God, the ultimate reality that governs the universe and sustains all existence."},

{"id": 464, "question": "What is the nature of God in Dharma?", "answer": "The nature of God in Dharma is understood as eternal, all-pervading, and the source of creation, preservation, and dissolution."},

{"id": 465, "question": "What is prayer discipline?", "answer": "Prayer discipline is the regular practice of prayer with sincerity, focus, and devotion as part of daily spiritual life."},

{"id": 466, "question": "What is daily spiritual practice?", "answer": "Daily spiritual practice includes prayer, meditation, self-reflection, and righteous living to maintain inner growth."},

{"id": 467, "question": "Why is self-reflection important daily?", "answer": "Self-reflection is important because it helps identify mistakes, improve conduct, and progress toward spiritual growth."},
{"id": 468, "question": "What is Guru?", "answer": "A Guru is a spiritual teacher who guides a seeker with knowledge, discipline, and wisdom toward understanding the truth."},

{"id": 469, "question": "Why is a Guru important?", "answer": "A Guru is important because they provide guidance, remove ignorance, and help the seeker progress safely on the spiritual path."},

{"id": 470, "question": "What is Shraddha?", "answer": "Shraddha is faith combined with respect and sincerity toward Dharma, scriptures, and the Guru."},

{"id": 471, "question": "What is Satsang?", "answer": "Satsang is the association with wise people and the study of truth, which helps elevate the mind and strengthen Dharma."},

{"id": 472, "question": "What is scriptural study?", "answer": "Scriptural study is the disciplined reading and understanding of sacred texts to gain knowledge of Dharma and spiritual truths."},

{"id": 473, "question": "What is Vairagya?", "answer": "Vairagya is detachment from worldly pleasures and desires, allowing focus on higher spiritual goals."},

{"id": 474, "question": "What is discrimination (Viveka)?", "answer": "Viveka is the ability to distinguish between what is permanent and impermanent, right and wrong, guiding one toward Dharma."},

{"id": 475, "question": "What is ego and why should it be reduced?", "answer": "Ego is the sense of self-importance and attachment to identity, which should be reduced to attain humility and spiritual clarity."},

{"id": 476, "question": "What is the importance of humility in spiritual life?", "answer": "Humility allows a person to learn, accept truth, and progress spiritually without being limited by pride."},

{"id": 477, "question": "What is renunciation?", "answer": "Renunciation is the voluntary letting go of attachments and desires to focus on spiritual growth and realization."}

]
EVIDENCE_MAP = {
    "What is Dharma?": "Manusmriti 1.108 (paraphrased): Dharma sustains and upholds the order of life and society.",
    "What is Moksha?": "Bhagavad Gita 2.51: The wise, freed from the cycle of birth and death, attain the highest state.",
    "What is Karma?": "Bhagavad Gita 4.17: 'Gahana karmano gatih' — the nature of action is profound and leads to consequences.",
    "What is truth (Satya)?": "Mahabharata: 'Satyam eva jayate' — Truth alone triumphs.",
    "What is non-violence (Ahimsa)?": "Mahabharata: 'Ahimsa paramo dharmah' — Non-violence is the highest Dharma.",
} 

def make_point(record: dict) -> PointStruct:
    text = f"Q: {record['question']}\nA: {record['answer']}"
    embedding = oa_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

    return PointStruct(
        id=record["id"],
        vector=embedding,
        payload={
            "question": record["question"],
            "answer": record["answer"],
            "evidence": record.get("evidence") or EVIDENCE_MAP.get(record["question"]), 
            "source_basis": "Dharma seed Q&A",
            "qualification": "General foundational definition."
        }
    )

points = [make_point(r) for r in records]

batch_size = 5
for i in range(0, len(points), batch_size):
    batch = points[i:i + batch_size]
    qdrant.upsert(
        collection_name=collection_name,
        points=batch,
        wait=True,
    )
    print(f"Uploaded batch {i // batch_size + 1}: {len(batch)} record(s)")
    time.sleep(1)

print("Ingestion completed successfully.")
