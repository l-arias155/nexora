import { Body, Controller, Get, Param, Post, UseGuards } from '@nestjs/common';
import { OrganizationsService } from './organizations.service.js';
import { CreateOrganizationDto } from './dto/create-organization.dto.js';
import { InviteMemberDto } from './dto/invite-member.dto.js';
import { JwtAuthGuard } from '../common/guards/jwt-auth.guard.js';
import { MembershipGuard } from '../common/guards/membership.guard.js';
import { Roles } from '../common/decorators/roles.decorator.js';
import { CurrentUser } from '../common/decorators/current-user.decorator.js';
import { MembershipRole } from '../generated/prisma/enums.js';
import type { AuthUser } from '../common/types/authenticated-request.js';

@Controller('organizations')
@UseGuards(JwtAuthGuard)
export class OrganizationsController {
  constructor(private readonly organizationsService: OrganizationsService) {}

  @Post()
  create(@CurrentUser() user: AuthUser, @Body() dto: CreateOrganizationDto) {
    return this.organizationsService.create(user.userId, dto);
  }

  @Get()
  findMine(@CurrentUser() user: AuthUser) {
    return this.organizationsService.findMine(user.userId);
  }

  @Get(':organizationId')
  @UseGuards(MembershipGuard)
  findOne(@Param('organizationId') organizationId: string) {
    return this.organizationsService.findOne(organizationId);
  }

  @Get(':organizationId/members')
  @UseGuards(MembershipGuard)
  listMembers(@Param('organizationId') organizationId: string) {
    return this.organizationsService.listMembers(organizationId);
  }

  @Post(':organizationId/members')
  @UseGuards(MembershipGuard)
  @Roles(MembershipRole.OWNER, MembershipRole.ADMIN)
  inviteMember(
    @Param('organizationId') organizationId: string,
    @Body() dto: InviteMemberDto,
  ) {
    return this.organizationsService.inviteMember(organizationId, dto);
  }
}
