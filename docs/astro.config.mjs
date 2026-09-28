// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({
      title: 'ScamShield Documentation',

      social: [
        {
          icon: 'github',
          label: 'GitHub',
            href: 'https://github.com/ashrafee-dev/scamshield-api',
        },
      ],

      sidebar: [
        {
          label: 'Contribute',
          items: [{ label: 'Start here', slug: 'contributing' }],
        },
        {
          label: 'Guides',
          items: [
            {
              label: 'Quick Start',
              slug: 'guides/quickstart',
            },
            { label: 'Deployment', slug: 'guides/deployment' },
            { label: 'Privacy and clients', slug: 'guides/privacy' },
          ],
        },
        {
          label: 'Reference',
          items: [
            {
              autogenerate: {
                directory: 'reference',
              },
            },
          ],
        },
      ],
    }),
  ],
});
