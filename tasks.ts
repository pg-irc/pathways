// intended to be located at pathways-frontend/src/fixtures/tasks.ts

import { Store } from './types/tasks';
export { Id, Task, TaskUserSettings, TaskMap, TaskUserSettingsMap, TaskList, Store } from './types/tasks';

export const buildTasksFixture = (): Store => {
    return {
        taskMap:         {
            "Getting involved": {
                "description": {
                    "en": "If you have a child in school, talk often with your child’s teachers. Go to the parent-teacher meetings during the year. You can also go to meetings and volunteer at the school. Your children will sometimes bring home letters and notices from school.\nThese letters may contain important information about events and changes in the school.",
                    "fr": "Si votre enfant va à l'école, communiquez souvent avec ses enseignants. Allez aux réunions parents-enseignants durant l'année.\nVous pouvez aussi aller aux réunions et faire du bénévolat à l'école. Vos enfants rapporteront parfois des lettres et des avis à la maison. Ces lettres peuvent comprendre des renseignements importants sur des évènements et des changements à l'école."
                },
                "id": "Getting involved",
                "title": {
                    "en": "Getting involved",
                    "fr": "S_impliquer"
                }
            },
            "Learn english": {
                "description": {
                    "en": "There are many English as a Second Language (ESL) classes to help adults learn to speak, read, and write English. The government oﬀers Language Instruction for Newcomers to Canada classes. Adult refugees and permanent residents can take these classes for free.\n[www.cic.gc.ca](http://www.cic.gc.ca/english/newcomers/live/language.asp)\n\n# College and public school English classes Adult immigrants can also attend full-time or part-time ESL classes. Seventeen public post-secondary institutions oﬀer ESL classes in B.C.\n[www2.gov.bc.ca](http://www2.gov.bc.ca/gov/content/educationtraining/adult-education/adult-upgrading-learn-english)\nThe provincial government oﬀers the Adult Upgrading Grant to help students with low incomes pay for tuition. Visit the website to learn more about grants and scholarships.\n[studentaidbc.ca](http://studentaidbc.ca/explore/grants-scholarships)\n\n# Private English schools and tutors Many private English schools and tutors also teach English. These classes may not be accredited with the provincial government. They may also be more expensive than those oﬀered in public schools and colleges.\n[bcteal.org](http://bcteal.org/esldirectory)",
                    "fr": "Il existe de nombreux cours d'anglais langue seconde (ALS) pour aider les adultes à apprendre à parler, à lire et à écrire en anglais.\nLe gouvernement oﬀre des cours de langue pour les nouveaux arrivants au Canada. Les réfugiés et les résidents permanents adultes peuvent suivre ces cours gratuitement.\n[www.cic.gc.ca](http://www.cic.gc.ca/english/newcomers/live/language.asp)\n\n# Cours d'anglais dans les collèges et les écoles publiques Les immigrants adultes peuvent aussi suivre des cours d'ALS à temps plein ou à temps partiel. Dix-sept institutions postsecondaires publiques oﬀrent des cours d'ALS en C.-B.\n[www2.gov.bc.ca](http://www2.gov.bc.ca/gov/content/educationtraining/adult-education/adult-upgrading-learn-english)\nLe gouvernement provincial oﬀre l'Adult Upgrading Grant pour aider les étudiants ayant des revenus modestes à payer les frais de scolarité. Visitez le site Web pour en savoir plus sur les subventions et les bourses.\n[studentaidbc.ca](http://studentaidbc.ca/explore/grants-scholarships)\n\n# Écoles privées et tuteurs de langue anglais Certaines écoles privées et tuteurs de langue anglaise enseignent aussi l'anglais. Ces cours peuvent ne pas être reconnus par le gouvernement provincial. Ils peuvent aussi être plus coûteux que ceux oﬀerts dans les écoles et les collèges publics.\n[bcteal.org](http://bcteal.org/esldirectory)"
                },
                "id": "Learn english",
                "title": {
                    "en": "Learn english",
                    "fr": "Apprendre l_anglais"
                }
            },
            "Registering your child in a public school": {
                "description": {
                    "en": "Children usually attend the public school closest to their home. To register your child in a public school, contact your school board. When you register your child, you will be asked to provide ofcial documents showing your child’s date of birth, your resident status in British Columbia, and the address where you live. You will also be asked to show your child’s immunization record. This is a paper that has information about vaccinations your children have received to protect them against diseases.\n\nSome school communities provide a program called Settlement Workers in Schools (SWIS). The workers in this program help the children of newcomers and their families adjust to their new school and community.",
                    "fr": "Les enfants fréquentent généralement l'école publique la plus proche de chez eux. Pour inscrire votre enfant dans une école publique,\ncontactez votre conseil scolaire. Quand vous inscrivez votre enfant, vous devez fournir des documents ofciels indiquant la date de naissance de votre enfant, votre statut de résidence en Colombie-Britannique et votre adresse. Vous devez aussi montrer le carnet de vaccination de votre enfant. Il s'agit d'un document donnant des renseignements sur les vaccins que votre enfant a reçus pour le protéger contre les maladies.\n\nCertaines communautés scolaires oﬀrent un programme appelé Travailleurs de l'établissement dans les écoles (TEE). Les travailleurs de ce programme aident les enfants des nouveaux arrivants et leur famille à s'ajuster à leur nouvelle école et à leur nouvelle communauté."
                },
                "id": "Registering your child in a public school",
                "title": {
                    "en": "Registering your child in a public school",
                    "fr": "Inscrire votre enfant dans une école publique"
                }
            },
            "Using a lawyer": {
                "description": {
                    "en": "If you have a legal problem, you may need a lawyer. Sometimes a lawyer can help you solve a problem before you go to court.\n\n# How to fnd a lawyer\n* Ask your friends.\n* Contact the Lawyer Referral Service.\nThis service will give you the name of a lawyer. The lawyer will talk to you for up to 30 minutes for $25 plus taxes.\nToll-free: 1 800 663-1919 [www.cbabc.org](http://www.cbabc.org/for-the-public/lawyer-referral-service)\n\n# Help if you cannot aﬀord a lawyer Legal aid is a free service for people who cannot aﬀord to hire a lawyer. Legal aid can help with some types of criminal law, family law, and immigration law problems. If you cannot aﬀord a lawyer, contact the Legal Services Society.\nMetro Vancouver: 604 408-2172 Toll-free: 1 866 577-2525 [www.lss.bc.ca](http://www.lss.bc.ca)\nAccess Pro Bono is a non-proft society that connects people with low incomes with volunteer lawyers for legal help. Their services are free.\nToll-free: 1 877 762-6664 [www.accessprobono.ca](http://www.accessprobono.ca)",
                    "fr": "En cas de problème juridique, vous aurez peut-\nêtre besoin d’un avocat. Un avocat peut parfois vous aider à régler un problème sans devoir aller au tribunal.\n\n# Comment trouver un avocat?\n* Demandez à vos amis\n* Contactez le Service de renvoi à un avocat. Ce service vous donnera le nom d’un avocat. Cet avocat vous accordera jusqu’à 30 minutes pour 25 $ plus taxes.\nSans frais : 1 800 663-1919 [www.cbabc.org](http://www.cbabc.org/for-the-public/lawyer-referral-service)\n\n# Aide si un avocat est trop cher L’aide juridique est un service gratuit pour les gens qui ne peuvent pas se payer les services d’un avocat. L’aide juridique peut être utile en cas de problèmes avec certains cas de droit pénal, familial et de l’immigration. Si vous ne pouvez pas payer les services d’un avocat,\ncontactez la Legal Services Society.\nMetro Vancouver : 604 408-2172 Sans frais : 1 866 577-2525 [www.lss.bc.ca](http://www.lss.bc.ca)\nAccess Pro Bono est une société sans but lucratif qui connecte les personnes à faibles revenus à des avocats bénévoles pour obtenir de l’aide juridique gratuite.\nSans frais : 1 877 762-6664 [www.accessprobono.ca](http://www.accessprobono.ca)"
                },
                "id": "Using a lawyer",
                "title": {
                    "en": "Using a lawyer",
                    "fr": "Avoir recours à un avocat"
                }
            }
        }
    }
}