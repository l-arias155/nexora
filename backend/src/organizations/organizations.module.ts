import { Module } from '@nestjs/common';
import { OrganizationsController } from './organizations.controller.js';
import { OrganizationsService } from './organizations.service.js';
import { MembershipGuard } from '../common/guards/membership.guard.js';

@Module({
  controllers: [OrganizationsController],
  providers: [OrganizationsService, MembershipGuard],
  exports: [OrganizationsService],
})
export class OrganizationsModule {}
